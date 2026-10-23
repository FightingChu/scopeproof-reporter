import tempfile
import unittest
from pathlib import Path

from scopeproof.io import atomic_write_text


class IoTests(unittest.TestCase):
    def test_atomic_write_replaces_complete_content(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "report.md"
            atomic_write_text(path, "first\n")
            atomic_write_text(path, "second\n")
            self.assertEqual("second\n", path.read_text(encoding="utf-8"))
            self.assertEqual([], list(path.parent.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
