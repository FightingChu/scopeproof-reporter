import unittest

from scopeproof.redact import REDACTED, redact_text


class RedactionTests(unittest.TestCase):
    def test_redacts_header_and_assignments(self):
        source = "Authorization: Bearer TOKEN-123456\npassword=hunter2\napi_key=abcdef123456"
        result = redact_text(source)
        self.assertNotIn("TOKEN-123456", result)
        self.assertNotIn("hunter2", result)
        self.assertNotIn("abcdef123456", result)
        self.assertEqual(3, result.count(REDACTED))

    def test_redacts_cookie_line(self):
        self.assertEqual("Cookie: [REDACTED]", redact_text("Cookie: sid=abc123456"))


if __name__ == "__main__":
    unittest.main()
