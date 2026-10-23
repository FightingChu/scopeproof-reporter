import unittest

from scopeproof.catalog import RuleCatalog
from scopeproof.models import ValidationError
from tests.support import ROOT


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = RuleCatalog.load(ROOT / "catalog" / "rules")

    def test_known_rule_is_available(self):
        self.assertEqual("authentication", self.catalog.get("SP-AUTH-001").family)

    def test_unknown_rule_is_explicit(self):
        with self.assertRaisesRegex(ValidationError, "unknown rule id"):
            self.catalog.get("SP-NOT-FOUND-999")


if __name__ == "__main__":
    unittest.main()
