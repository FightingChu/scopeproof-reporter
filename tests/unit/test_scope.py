import unittest

from scopeproof.models import ValidationError
from scopeproof.scope import require_authorized_asset
from tests.support import scope


class ScopeTests(unittest.TestCase):
    def test_authorized_asset_passes(self):
        require_authorized_asset(scope(), "portal.example.test")

    def test_unknown_asset_fails(self):
        with self.assertRaisesRegex(ValidationError, "not listed in scope"):
            require_authorized_asset(scope(), "outside.example.test")


if __name__ == "__main__":
    unittest.main()
