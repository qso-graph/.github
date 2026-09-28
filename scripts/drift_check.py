#!/usr/bin/env python3
"""Publishing drift check for every qso-graph MCP.

A release is done only when it's published everywhere (TEMPLATES.md). This
compares, for every repo with a server.json:

- the latest release tag on GitHub
- PyPI
- the Official MCP Registry
- the Homebrew tap (qso-graph/homebrew-mcp)

and reports any server where they disagree. Standard library only.

Output: a Markdown table on stdout (for the job summary). Exit status 10 if
anything drifted (10, not 1: a crash exits 1), so the workflow can open or
update the drift issue.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ORG = "qso-graph"
TAP = "homebrew-mcp"
REGISTRY = "https://registry.modelcontextprotocol.io/v0/servers"
UA = "qso-graph-drift-check (+https://github.com/qso-graph/.github)"
DRIFT = 10  # distinct from 1, which is what a crash exits with
VERSION_TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")


def get(url: str, token: bool = False) -> bytes | None:
    """GET a URL; None on 404."""
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token and os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(1, 4):  # the services are sometimes slow; retry before giving up
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code < 500 or attempt == 3:
                raise
        except (urllib.error.URLError, TimeoutError, OSError):
            if attempt == 3:
                raise
        time.sleep(5 * attempt)
    return None


def get_json(url: str, token: bool = False):
    body = get(url, token)
    return json.loads(body) if body is not None else None


def version_key(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def mcp_repos() -> tuple[list[str], list[str]]:
    """(repos with a server.json, *-mcp repos without one). Public, unarchived only.

    A server without a server.json can never reach the Registry, so it's
    reported rather than silently skipped.
    """
    repos, page = [], 1
    while True:
        batch = get_json(f"https://api.github.com/orgs/{ORG}/repos?per_page=100&page={page}", token=True)
        if not batch:
            break
        repos += [r["name"] for r in batch if not r["archived"] and not r["private"]]
        page += 1
    with_sj = sorted(r for r in repos if get_json(f"https://api.github.com/repos/{ORG}/{r}/contents/server.json", token=True))
    missing = sorted(r for r in repos if r.endswith("-mcp") and r != TAP and r not in with_sj)
    return with_sj, missing


def server_json(repo: str) -> dict:
    meta = get_json(f"https://api.github.com/repos/{ORG}/{repo}/contents/server.json", token=True)
    return json.loads(base64.b64decode(meta["content"]))


def latest_tag(repo: str) -> str | None:
    tags = get_json(f"https://api.github.com/repos/{ORG}/{repo}/tags?per_page=100", token=True) or []
    versions = [m.group(1) for t in tags if (m := VERSION_TAG.match(t["name"]))]
    return max(versions, key=version_key) if versions else None


def pypi(package: str) -> str | None:
    data = get_json(f"https://pypi.org/pypi/{urllib.parse.quote(package)}/json")
    return data["info"]["version"] if data else None


def registry(name: str) -> str | None:
    q = urllib.parse.urlencode({"search": name, "version": "latest"})
    data = get_json(f"{REGISTRY}?{q}") or {}
    for s in data.get("servers", []):
        if s["server"]["name"] == name:
            return s["server"]["version"]
    return None


def homebrew(package: str) -> str | None:
    body = get(f"https://raw.githubusercontent.com/{ORG}/{TAP}/main/Formula/{package}.rb")
    if body is None:
        return None
    m = re.search(r'^\s*url\s+"[^"]*?-(\d+\.\d+\.\d+)\.tar\.gz"', body.decode(), re.MULTILINE)
    return m.group(1) if m else "unreadable"


def main() -> int:
    rows, drifted = [], []
    with_sj, missing = mcp_repos()
    for repo in with_sj:
        sj = server_json(repo)
        package = sj["packages"][0]["identifier"]
        lookups = {
            "tag": lambda: latest_tag(repo),
            "PyPI": lambda: pypi(package),
            "Registry": lambda: registry(sj["name"]),
            "Homebrew": lambda: homebrew(package),
        }
        found = {}
        for where, lookup in lookups.items():
            try:
                found[where] = lookup()
            except Exception as e:  # a service down is reported, not a crash
                print(f"{repo}: {where} unreachable: {e}", file=sys.stderr)
                found[where] = "unreachable"
        want = found["PyPI"] if found["PyPI"] not in (None, "unreachable") else found["tag"]
        bad = [where for where, v in found.items() if v != want]
        rows.append((repo, found, bad))
        if bad:
            drifted.append(repo)

    print("| Server | tag | PyPI | Registry | Homebrew | |")
    print("|---|---|---|---|---|---|")
    for repo, found, bad in rows:
        cells = [f"**{v or 'none'}**" if where in bad else (v or "none") for where, v in found.items()]
        print(f"| {repo} | " + " | ".join(cells) + f" | {'drift: ' + ', '.join(bad) if bad else 'ok'} |")
    for repo in missing:
        print(f"| {repo} | | | | | **no server.json** |")
        drifted.append(repo)
    print()
    if drifted:
        print(f"**{len(drifted)} of {len(rows) + len(missing)} servers have drifted:** {', '.join(drifted)}. "
              "A release is done only when it's published everywhere (TEMPLATES.md).")
    else:
        print(f"All {len(rows)} servers are published everywhere.")
    return DRIFT if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
