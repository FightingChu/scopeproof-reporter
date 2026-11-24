import unittest

from scopeproof.catalog import RuleCatalog
from scopeproof.models import ValidationError
from scopeproof.profiles import AssessmentProfile, ProfileCatalog
from scopeproof.service import compile_report, validate_inputs
from tests.support import ROOT


class ProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = ProfileCatalog.load(
            ROOT / "profiles",
            RuleCatalog.load(ROOT / "catalog" / "rules").families(),
        )

    def test_loads_curated_profile(self):
        profile = self.catalog.get("profile-browser-application")
        self.assertEqual("Browser application review", profile.title)
        self.assertIn("authentication", profile.families)

    def test_rejects_duplicate_profile_families(self):
        with self.assertRaisesRegex(ValidationError, "must be unique"):
            AssessmentProfile.from_dict({
                "id": "profile-test",
                "title": "Test profile",
                "families": ["authentication", "authentication"],
            })

    def test_rejects_unknown_profile_family(self):
        profile = AssessmentProfile("profile-test", "Test profile", ("unknown",))
        with self.assertRaisesRegex(ValidationError, "unknown families"):
            ProfileCatalog([profile], {"authentication"})

    def test_evidence_outside_profile_fails_closed(self):
        with self.assertRaisesRegex(ValidationError, "outside profile"):
            validate_inputs(
                ROOT / "examples" / "scope.json",
                ROOT / "examples" / "evidence" / "configuration.json",
                profile_id="profile-browser-application",
            )

    def test_supported_profile_accepts_evidence(self):
        _, findings = validate_inputs(
            ROOT / "examples" / "scope.json",
            ROOT / "examples" / "evidence" / "authentication.json",
            profile_id="profile-browser-application",
        )
        self.assertEqual(["SP-AUTH-001"], [finding.rule.id for finding in findings])

    def test_report_records_selected_profile(self):
        destination = ROOT / "output" / "profile-report.md"
        try:
            compile_report(
                ROOT / "examples" / "scope.json",
                ROOT / "examples" / "evidence" / "authentication.json",
                destination,
                profile_id="profile-browser-application",
            )
            report = destination.read_text(encoding="utf-8")
            self.assertIn("Assessment profile: `Browser application review`", report)
        finally:
            destination.unlink(missing_ok=True)
            if destination.parent.exists() and not any(destination.parent.iterdir()):
                destination.parent.rmdir()


if __name__ == "__main__":
    unittest.main()
