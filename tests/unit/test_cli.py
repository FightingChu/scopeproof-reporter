import contextlib
import io
import json
import unittest

from scopeproof.cli import main
from tests.support import ROOT


class CliTests(unittest.TestCase):
    def invoke(self, arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = main(arguments)
        return result, stdout.getvalue(), stderr.getvalue()

    def test_validate_json_emits_deterministic_safe_summary(self):
        arguments = [
            "validate",
            "--scope",
            str(ROOT / "examples" / "scope.json"),
            "--evidence",
            str(ROOT / "examples" / "evidence"),
            "--json",
        ]
        result, stdout, stderr = self.invoke(arguments)
        self.assertEqual(0, result, stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(2, payload["evidence_count"])
        self.assertEqual({"high": 1, "medium": 1, "critical": 0, "info": 0, "low": 0}, payload["counts_by_severity"])
        self.assertEqual({"confirmed": 1, "needs-review": 1, "not-observed": 0}, payload["counts_by_status"])
        self.assertEqual({"authentication": 1, "configuration": 1}, payload["counts_by_family"])
        self.assertEqual(
            ["EV-DEMO-CONFIG-001", "EV-DEMO-AUTH-001"],
            [item["evidence_id"] for item in payload["findings"]],
        )
        self.assertNotIn("observation", stdout)
        self.assertNotIn("request", stdout)
        self.assertNotIn("response", stdout)

    def test_validate_profile_json_limits_findings(self):
        result, stdout, stderr = self.invoke([
            "validate",
            "--scope",
            str(ROOT / "examples" / "scope.json"),
            "--evidence",
            str(ROOT / "examples" / "evidence" / "authentication.json"),
            "--profile",
            "profile-browser-application",
            "--json",
        ])
        self.assertEqual(0, result, stderr)
        payload = json.loads(stdout)
        self.assertEqual(1, payload["evidence_count"])
        self.assertEqual("authentication", payload["findings"][0]["family"])

    def test_invalid_json_validation_stays_on_stderr(self):
        result, stdout, stderr = self.invoke([
            "validate",
            "--scope",
            str(ROOT / "examples" / "scope.json"),
            "--evidence",
            str(ROOT / "examples" / "evidence" / "configuration.json"),
            "--profile",
            "profile-browser-application",
            "--json",
        ])
        self.assertEqual(2, result)
        self.assertEqual("", stdout)
        self.assertIn("outside profile", stderr)


if __name__ == "__main__":
    unittest.main()
