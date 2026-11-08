import unittest

import conformance as c


class RulesTest(unittest.TestCase):
    def test_vale_json_counts_severities_across_files(self):
        sample = '''{
          "README.md": [{"Severity": "error"}, {"Severity": "warning"}, {"Severity": "suggestion"}],
          "docs/user/guide.md": [{"Severity": "error"}, {"Severity": "warning"}, {"Severity": "warning"}],
          "docs/user/empty.md": []
        }'''
        self.assertEqual(c.parse_vale_output(sample), (2, 3))
        self.assertEqual(c.parse_vale_output("{}"), (0, 0))

    def test_topics(self):
        self.assertTrue(c.topics_ok("qso-graph-desktop", ["qso-graph", "qso-graph-app", "radio"]))
        self.assertFalse(c.topics_ok("qso-graph-desktop", ["qso-graph", "qso-graph-mcp"]))
        self.assertTrue(c.topics_ok("qso-graph-trust", ["qso-graph", "qso-graph-app", "qso-graph-library"]))
        self.assertFalse(c.topics_ok("solar-mcp", ["qso-graph"]))
        self.assertFalse(c.topics_ok("homebrew-tap", ["qso-graph", "qso-graph-infra", "qso-graph-tool"]))
        self.assertFalse(c.topics_ok("solar-mcp", ["qso-graph-mcp"]))
        self.assertEqual(c.expected_section("example-demo"), "qso-graph-infra")

    def test_docs(self):
        self.assertTrue(c.docs_ok({"docs/user/guide.md", "docs/user/img/map.svg", "docs/dev.pdf"}))
        self.assertFalse(c.docs_ok({"docs/user/nested/index.md"}))
        self.assertFalse(c.docs_ok({"docs/user/archive.zip"}))

    def test_declared_license(self):
        self.assertTrue(c.declared_license_ok({"pyproject.toml": 'license = {text = "GPL-3.0-or-later"}'}))
        self.assertTrue(c.declared_license_ok({"Cargo.toml": 'license = "GPL-3.0-or-later"', "package.json": '"license": "GPL-3.0-or-later",'}))
        self.assertFalse(c.declared_license_ok({"Cargo.toml": 'license = "GPL-3.0-only"'}))
        self.assertFalse(c.declared_license_ok({"package.json": '"license": "GPL-3.0-only",'}))
        self.assertTrue(c.declared_license_ok({}))

    def test_install(self):
        self.assertFalse(c.install_ok({"pyproject.toml"}, "python -m pip install package"))
        self.assertTrue(c.install_ok({"pyproject.toml"}, "uvx package"))
        self.assertTrue(c.install_ok(set(), "pip install package"))
        for planted in ("pipx install package", "pip uninstall old && pip install new",
                        "pip3 install package", "python3 -m pip install package"):
            self.assertFalse(c.install_ok({"pyproject.toml"}, planted), planted)
        self.assertTrue(c.install_ok({"pyproject.toml"}, "uv tool install package; uv add package"))
        self.assertFalse(c.install_ok({"pyproject.toml"}, "Installed with pip instead? Use the command."))
        self.assertFalse(c.install_ok({"pyproject.toml"}, "which `pip` installs with it"))
        self.assertTrue(c.install_ok({"pyproject.toml"}, "CI runs pip-audit --strict."))

    def test_issue_forms(self):
        bug = "\n".join(f"      label: {label}" for label in c.BUG)
        feature = "\n".join(f"      label: {label}" for label in c.FEATURE)
        self.assertTrue(c.issue_templates_ok({}))
        self.assertTrue(c.issue_templates_ok({"bug.yml": bug, "feature.yml": feature}))
        self.assertFalse(c.issue_templates_ok({"config.yml": "blank_issues_enabled: false"}))
        self.assertFalse(c.issue_templates_ok({"bug.yml": bug}))

    def test_agent_guide(self):
        block = c.canonical_block()
        self.assertTrue(c.agent_guide_ok(b"# Guide\n" + block + b"\nOther text", block))
        self.assertFalse(c.agent_guide_ok(b"", block))
        self.assertFalse(c.agent_guide_ok(block.replace(b"credentials", b"secrets", 1), block))
        self.assertFalse(c.agent_guide_ok(block + block, block))
        self.assertFalse(c.agent_guide_ok(block.replace(b"\n", b"\r\n"), block))

    def test_pr_template(self):
        self.assertTrue(c.pr_templates_ok({}))
        self.assertTrue(c.pr_templates_ok({"pr.md": "## Issues\n## What changed\n## Verification\n## Credentials\n"}))
        self.assertFalse(c.pr_templates_ok({"pr.md": "## What changed\n"}))


if __name__ == "__main__":
    unittest.main()
