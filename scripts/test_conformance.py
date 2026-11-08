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
        self.assertFalse(c.topics_ok("solar-mcp", ["qso-graph", "qso-graph-mcp", "qso-graph-tool"]))
        self.assertFalse(c.topics_ok("solar-mcp", ["qso-graph-mcp"]))
        self.assertEqual(c.expected_section("example-demo"), "qso-graph-infra")

    def test_docs(self):
        self.assertTrue(c.docs_ok({"docs/user/guide.md", "docs/user/img/map.svg", "docs/dev.pdf"}))
        self.assertFalse(c.docs_ok({"docs/user/nested/index.md"}))
        self.assertFalse(c.docs_ok({"docs/user/archive.zip"}))

    def test_install(self):
        self.assertFalse(c.install_ok({"pyproject.toml"}, "python -m pip install package"))
        self.assertTrue(c.install_ok({"pyproject.toml"}, "uvx package"))
        self.assertTrue(c.install_ok(set(), "pip install package"))

    def test_issue_forms(self):
        bug = "\n".join(f"      label: {label}" for label in c.BUG)
        feature = "\n".join(f"      label: {label}" for label in c.FEATURE)
        self.assertTrue(c.issue_templates_ok({}))
        self.assertTrue(c.issue_templates_ok({"bug.yml": bug, "feature.yml": feature}))
        self.assertFalse(c.issue_templates_ok({"config.yml": "blank_issues_enabled: false"}))
        self.assertFalse(c.issue_templates_ok({"bug.yml": bug}))

    def test_pr_template(self):
        self.assertTrue(c.pr_templates_ok({}))
        self.assertTrue(c.pr_templates_ok({"pr.md": "## Issues\n## What changed\n## Verification\n## Credentials\n"}))
        self.assertFalse(c.pr_templates_ok({"pr.md": "## What changed\n"}))


if __name__ == "__main__":
    unittest.main()
