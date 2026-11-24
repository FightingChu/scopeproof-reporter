import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from scopeproof.report import build_markdown
from scopeproof.service import compile_report
from tests.support import ROOT, finding, scope


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

    def test_compiled_report_summarizes_rule_families(self):
        with tempfile.TemporaryDirectory() as folder:
            report_path = Path(folder) / "report.md"
            compile_report(
                ROOT / "examples" / "scope.json",
                ROOT / "examples" / "evidence",
                report_path,
            )
            report = report_path.read_text(encoding="utf-8")
            self.assertIn("## Findings by rule family", report)
            self.assertIn("| authentication | 1 |", report)
            self.assertIn("| configuration | 1 |", report)
            self.assertLess(
                report.index("Total findings: **2**"),
                report.index("## Findings by rule family"),
            )

    def test_compiled_reports_include_ordered_evidence_context(self):
        authentication = json.loads(
            (ROOT / "examples" / "evidence" / "authentication.json").read_text(encoding="utf-8")
        )
        configuration = json.loads(
            (ROOT / "examples" / "evidence" / "configuration.json").read_text(encoding="utf-8")
        )
        authentication["summary"] = "Bearer AUTH-SUMMARY-123456 leaked"
        configuration["summary"] = "api_key=CONFIG-SUMMARY-123456 ```"

        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            evidence_directory = temporary / "evidence"
            evidence_directory.mkdir()
            (evidence_directory / "authentication.json").write_text(
                json.dumps(authentication), encoding="utf-8"
            )
            (evidence_directory / "configuration.json").write_text(
                json.dumps(configuration), encoding="utf-8"
            )

            for output_format in ("markdown", "html"):
                report_path = temporary / f"report.{output_format}"
                compile_report(
                    ROOT / "examples" / "scope.json",
                    evidence_directory,
                    report_path,
                    output_format=output_format,
                )
                report = report_path.read_text(encoding="utf-8")
                if output_format == "markdown":
                    configuration_start = report.index("## 1. Production diagnostic detail exposure")
                    authentication_start = report.index("## 2. Login response account disclosure")
                else:
                    configuration_start = report.index("1. Production diagnostic detail exposure</h2>")
                    authentication_start = report.index("2. Login response account disclosure</h2>")
                configuration_section = report[configuration_start:authentication_start]
                authentication_section = report[authentication_start:]

                self.assertIn("EV-DEMO-CONFIG-001", configuration_section)
                self.assertIn("2026-10-10T11:00:00+00:00", configuration_section)
                self.assertIn("api_key=[REDACTED] ```", configuration_section)
                self.assertIn("EV-DEMO-AUTH-001", authentication_section)
                self.assertIn("2026-10-10T10:30:00+00:00", authentication_section)
                self.assertIn("Bearer [REDACTED] leaked", authentication_section)
                self.assertNotIn("CONFIG-SUMMARY-123456", report)
                self.assertNotIn("AUTH-SUMMARY-123456", report)
                if output_format == "markdown":
                    self.assertIn("````text", configuration_section)
                else:
                    self.assertIn("<pre>", configuration_section)

    def test_rule_family_summary_escapes_markdown_table_delimiters(self):
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder)
            evidence_data = json.loads(
                (ROOT / "examples" / "evidence" / "authentication.json").read_text(encoding="utf-8")
            )
            scope_data = json.loads((ROOT / "examples" / "scope.json").read_text(encoding="utf-8"))
            rule_data = json.loads(
                (ROOT / "catalog" / "rules" / "authentication" / "sp-auth-001.json").read_text(encoding="utf-8")
            )
            rule_data["family"] = "auth|entication"
            evidence_path = temporary / "evidence.json"
            scope_path = temporary / "scope.json"
            catalog_path = temporary / "catalog"
            catalog_path.mkdir()
            report_path = temporary / "report.md"
            evidence_path.write_text(json.dumps(evidence_data), encoding="utf-8")
            scope_path.write_text(json.dumps(scope_data), encoding="utf-8")
            (catalog_path / "rule.json").write_text(json.dumps(rule_data), encoding="utf-8")
            compile_report(scope_path, evidence_path, report_path, catalog_path=catalog_path)
            report = report_path.read_text(encoding="utf-8")
            self.assertIn(r"| auth\|entication | 1 |", report)


if __name__ == "__main__":
    unittest.main()
