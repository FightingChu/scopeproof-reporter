import unittest

from scopeproof.models import Evidence, ScopeManifest, ValidationError


class ModelTests(unittest.TestCase):
    def test_scope_rejects_reversed_dates(self):
        with self.assertRaisesRegex(ValidationError, "must not precede"):
            ScopeManifest.from_dict({
                "assessment_id": "A-1", "organization": "Example", "engagement": "Review",
                "authorized_assets": ["portal.example.test"], "valid_from": "2026-10-02",
                "valid_until": "2026-10-01", "owner": "Security"
            })

    def test_evidence_keeps_reproduction_order(self):
        record = Evidence.from_dict({
            "id": "EV-1", "rule_id": "SP-AUTH-001", "asset": "portal.example.test",
            "observed_at": "2026-10-01T00:00:00Z", "status": "confirmed",
            "summary": "Summary", "observation": "Observation",
            "reproduction": ["step one", "step two"], "confidence": "high"
        })
        self.assertEqual(("step one", "step two"), record.reproduction)


if __name__ == "__main__":
    unittest.main()
