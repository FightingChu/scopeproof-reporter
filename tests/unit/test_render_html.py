import unittest

from scopeproof.render_html import markdown_to_html


class HtmlTests(unittest.TestCase):
    def test_escapes_markup_in_paragraphs_and_code(self):
        rendered = markdown_to_html("# Title\n\n<script>alert(1)</script>\n\n```text\n<a>&\n```\n")
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;a&gt;&amp;", rendered)


if __name__ == "__main__":
    unittest.main()
