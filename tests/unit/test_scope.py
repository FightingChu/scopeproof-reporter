import unittest
from dataclasses import replace
from datetime import date, datetime, timezone

from scopeproof.models import ValidationError
from scopeproof.scope import require_authorized_asset, require_evidence_in_scope
from tests.support import evidence, scope


class ScopeTests(unittest.TestCase):
    def test_authorized_asset_passes(self):
        require_authorized_asset(scope(), "portal.example.test")

    def test_unknown_asset_fails(self):
        with self.assertRaisesRegex(ValidationError, "not listed in scope"):
            require_authorized_asset(scope(), "outside.example.test")

    def test_first_and_last_scope_dates_are_inclusive(self):
        manifest = scope()
        for observed_date in (manifest.valid_from, manifest.valid_until):
            record = replace(
                evidence(),
                observed_at=datetime.combine(observed_date, datetime.min.time(), timezone.utc),
            )
            require_evidence_in_scope(manifest, record)

    def test_evidence_before_scope_is_rejected(self):
        record = replace(
            evidence(),
            observed_at=datetime.combine(date(2026, 9, 30), datetime.min.time(), timezone.utc),
        )
        with self.assertRaisesRegex(ValidationError, "falls outside scope validity"):
            require_evidence_in_scope(scope(), record)

    def test_evidence_after_scope_is_rejected(self):
        record = replace(
            evidence(),
            observed_at=datetime.combine(date(2026, 11, 1), datetime.min.time(), timezone.utc),
        )
        with self.assertRaisesRegex(ValidationError, "falls outside scope validity"):
            require_evidence_in_scope(scope(), record)


if __name__ == "__main__":
    unittest.main()
