import unittest

from scopeproof.models import ValidationError
from scopeproof.templates import TemplateLibrary
from tests.support import ROOT


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.library = TemplateLibrary(ROOT / "templates")

    def test_lists_and_reads_known_template(self):
        self.assertIn("finding", self.library.names())
        self.assertIn("{{ title }}", self.library.read("finding"))

    def test_rejects_traversal(self):
        with self.assertRaises(ValidationError):
            self.library.read("../TASK")


if __name__ == "__main__":
    unittest.main()
