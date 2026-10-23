import tempfile
import unittest
from pathlib import Path

from scopeproof.models import ValidationError
from scopeproof.schema import load_json_object


class SchemaTests(unittest.TestCase):
    def test_loads_object(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "value.json"
            path.write_text('{"key": "value"}', encoding="utf-8")
            self.assertEqual({"key": "value"}, load_json_object(path))

    def test_rejects_array_root(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "value.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "must be an object"):
                load_json_object(path)


if __name__ == "__main__":
    unittest.main()
