#!/usr/bin/env python3
"""Report public repository conformance as a Markdown job summary.

Checks the default branch, except that CHANGELOG is required when a GitHub
Release exists. Report-only by default; --strict exits 10 for any finding.
"""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

ORG = "qso-graph"
API = "https://api.github.com"
SECTIONS = {f"qso-graph-{s}" for s in ("app", "mcp", "library", "tool", "infra")}
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".ico"}
BUG = {"Observed", "Reproduce", "Credentials"}
FEATURE = {"Summary", "Credentials"}
PR = {"Issues", "What changed", "Verification", "Credentials"}
COLUMNS = ("Topics", "Description", "License", "Changelog", "README", "Install", "User docs", "Style", "Issue templates", "PR template", "Private reporting")


def get_json(url: str):
    headers = {"User-Agent": "qso-graph-conformance", "Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            if error.code < 500 or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == 2:
                raise
        time.sleep(5 * (attempt + 1))


def expected_section(name: str) -> str | None:
    if name in {"qso-graph-desktop", "qso-graph-trust"}:
        return "qso-graph-app"
    if name in {"qso-graph-auth", "qso-graph-lib"}:
        return "qso-graph-library"
    if name in {"qso-graph-sim", "qsp-client", "qso-graph-sdk"}:
        return "qso-graph-tool"
    if name in {"homebrew-tap", "qso-graph-desktop-updates", "qso-graph-packages", "qso-graph.github.io", ".github"} or "demo" in name.lower():
        return "qso-graph-infra"
    if name.endswith("-mcp"):
        return "qso-graph-mcp"
    return None


def topics_ok(name: str, topics: list[str]) -> bool:
    sections = SECTIONS.intersection(topics)
    expected = expected_section(name)
    # At least one section; a repository can be more than one thing (QG Trust is an application and a
    # library). Infrastructure is never also a product.
    if "qso-graph-infra" in sections and len(sections) > 1:
        return False
    return "qso-graph" in topics and len(sections) >= 1 and (expected is None or expected in sections)


def docs_ok(paths: set[str]) -> bool:
    for path in paths:
        if path.startswith("docs/user/"):
            p = PurePosixPath(path)
            if p.name.lower() == "index.md" or p.suffix.lower() not in IMAGES | {".md"}:
                return False
    return True


# Any way of installing with pip rather than uv: pip or pip3 install/uninstall, python -m pip, pipx.
# Only `pip install` was matched until 2026-11, so `pipx install` and `pip uninstall` passed unseen.
PIP = re.compile(r"\b(?:pip3?\s+(?:install|uninstall)|python3?\s+-m\s+pip|pipx)\b", re.I)


def install_ok(paths: set[str], readme: str) -> bool:
    return "pyproject.toml" not in paths or PIP.search(readme) is None


def headings(text: str) -> set[str]:
    return set(re.findall(r"(?m)^##\s+(.+?)\s*#*\s*$", text))


def issue_labels(text: str) -> set[str]:
    # GitHub issue forms use label:; Markdown templates use headings.
    return {m.strip().strip("\"'") for m in re.findall(r"(?m)^\s+label:\s*(.+?)\s*$", text)} | headings(text)


def issue_templates_ok(files: dict[str, str]) -> bool:
    if not files:
        return True
    forms = [issue_labels(content) for path, content in files.items() if PurePosixPath(path).name not in {"config.yml", "config.yaml"}]
    return any(BUG <= labels for labels in forms) and any(FEATURE <= labels for labels in forms)


def pr_templates_ok(files: dict[str, str]) -> bool:
    return not files or all(PR <= headings(content) for content in files.values())


def repositories() -> list[dict]:
    repos, page = [], 1
    while True:
        batch = get_json(f"{API}/orgs/{ORG}/repos?per_page=100&page={page}")
        if not batch:
            return sorted(repos, key=lambda r: r["name"].lower())
        repos.extend(r for r in batch if not r["private"] and not r["archived"])
        page += 1


def parse_vale_output(output: str) -> tuple[int, int]:
    """Count error and warning alerts in Vale's JSON output."""
    alerts = json.loads(output)
    errors = warnings = 0
    for file_alerts in alerts.values():
        for alert in file_alerts:
            severity = alert["Severity"].lower()
            errors += severity == "error"
            warnings += severity == "warning"
    return errors, warnings


def check_style(files: dict[str, str], vale: str) -> tuple[int, int]:
    if not files:
        return 0, 0
    config = Path(__file__).resolve().parent.parent / ".vale.ini"
    with tempfile.TemporaryDirectory(prefix="qso-graph-vale-") as directory:
        root = Path(directory)
        for index, (name, text) in enumerate(files.items()):
            # Vale discovers lowercase .md files; normalize other Markdown extensions.
            target = root / str(index) / (PurePosixPath(name).stem + ".md")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        result = subprocess.run(
            [vale, "--config", str(config), "--output=JSON", str(root)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        if result.returncode not in (0, 1):
            raise RuntimeError(f"Vale failed: {result.stderr.strip()}")
        try:
            return parse_vale_output(result.stdout)
        except (ValueError, KeyError, TypeError) as error:
            raise RuntimeError(f"Invalid Vale output: {result.stderr.strip()}") from error


def inspect(repo: dict, vale: str | None = None) -> tuple[str, dict, int]:
    name = repo["name"]
    base = f"{API}/repos/{ORG}/{urllib.parse.quote(name, safe='')}"
    branch = urllib.parse.quote(repo["default_branch"], safe="")
    tree = get_json(f"{base}/git/trees/{branch}?recursive=1")
    if not tree or tree.get("truncated"):
        raise RuntimeError(f"Cannot inspect complete tree for {name}")
    blobs = {item["path"]: item for item in tree["tree"] if item["type"] == "blob"}
    paths = set(blobs)

    def content(path: str) -> str:
        data = get_json(blobs[path]["url"])
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")

    readme = content("README.md") if "README.md" in paths else ""
    style_files = {}
    if vale:
        if "README.md" in paths:
            style_files["README.md"] = readme
        style_files.update({p: content(p) for p in sorted(paths) if p.startswith("docs/user/") and PurePosixPath(p).suffix.lower() == ".md"})
    errors, warnings = check_style(style_files, vale) if vale else (0, 0)
    issues = {p: content(p) for p in paths if p.startswith(".github/ISSUE_TEMPLATE/") and PurePosixPath(p).suffix.lower() in {".md", ".yml", ".yaml"}}

    prs = {p: content(p) for p in paths if p.lower() in {"pull_request_template.md", "docs/pull_request_template.md", ".github/pull_request_template.md"} or p.lower().startswith(".github/pull_request_template/") and p.lower().endswith(".md")}
    releases = get_json(f"{base}/releases?per_page=100") or []
    released = any(not release["draft"] for release in releases)
    license_data = get_json(f"{base}/license") if "LICENSE" in paths else None
    checks = {
        "Topics": topics_ok(name, repo.get("topics", [])),
        "Description": bool((repo.get("description") or "").strip()),
        "License": bool(license_data and (license_data.get("license") or {}).get("spdx_id") == "GPL-3.0"),
        "Changelog": not released or "CHANGELOG.md" in paths,
        "README": "README.md" in paths,
        "Install": install_ok(paths, readme),
        "User docs": docs_ok(paths),
        "Style": None if not vale else errors,
        "Issue templates": issue_templates_ok(issues),
        "PR template": pr_templates_ok(prs),
        # SECURITY.md sends reporters to the repository's private vulnerability reporting, so it
        # must be switched on; the setting is readable on a public repository with no token.
        "Private reporting": bool((get_json(f"{base}/private-vulnerability-reporting") or {}).get("enabled")),
    }
    return name, checks, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit 10 if any rule fails")
    args = parser.parse_args()
    vale = shutil.which("vale")
    with ThreadPoolExecutor(max_workers=6) as executor:
        rows = list(executor.map(lambda repo: inspect(repo, vale), repositories()))
    print("| Repository | " + " | ".join(COLUMNS) + " | Failures |")
    print("|---|" + "---|" * (len(COLUMNS) + 1))
    failed = 0
    warning_count = 0
    for name, checks, warnings in rows:
        warning_count += warnings
        bad = [column for column in COLUMNS
               if (checks[column] is not None and checks[column] > 0)
               if column == "Style"]
        bad += [column for column in COLUMNS if column != "Style" and not checks[column]]
        failed += bool(bad)
        def cell(column: str) -> str:
            value = checks[column]
            if column == "Style":
                return "skipped" if value is None else f"{value} errors" if value else "ok"
            return "ok" if value else "FAIL"
        print(f"| {name} | " + " | ".join(cell(c) for c in COLUMNS) + " | " + (", ".join(bad) or "—") + " |")
    print(f"\n{failed} of {len(rows)} repositories have findings. Checks inspect the default branch; releases include prereleases.")
    print(f"Style: {warning_count} warning alerts across all repositories; warnings do not fail the check." if vale else "Style: skipped because Vale is not on PATH.")
    return 10 if args.strict and failed else 0


if __name__ == "__main__":
    sys.exit(main())
