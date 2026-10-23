import unittest

from scopeproof.report import build_markdown
from tests.support import finding, scope


class ReportTests(unittest.TestCase):
    def test_report_contains_scope_and_summary(self):
        report = build_markdown(scope(), [finding()])
        self.assertIn("ASSESS-TEST-001", report)
        self.assertIn("portal.example.test", report)
        self.assertIn("| Medium | 1 |", report)

    def test_protocol_excerpts_are_redacted(self):
        report = build_markdown(scope(), [finding()])
        self.assertNotIn("SAMPLE-TOKEN-12345", report)
        self.assertNotIn("SESSION-12345", report)
        self.assertIn("[REDACTED]", report)


if __name__ == "__main__":
    unittest.main()
