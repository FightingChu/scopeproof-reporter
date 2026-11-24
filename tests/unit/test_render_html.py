import unittest

from scopeproof.render_html import markdown_to_html


class HtmlTests(unittest.TestCase):
    def test_escapes_markup_in_paragraphs_and_code(self):
        rendered = markdown_to_html("# Title\n\n<script>alert(1)</script>\n\n```text\n<a>&\n```\n")
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;a&gt;&amp;", rendered)

    def test_generates_navigable_contents_for_report_sections(self):
        rendered = markdown_to_html("# Report\n\n## Authorized scope\n\n## 1. Login <review>\n")
        self.assertIn('<nav class="report-toc" aria-label="Report contents">', rendered)
        self.assertIn('<a href="#section-1">Authorized scope</a>', rendered)
        self.assertIn('<h2 id="section-1">Authorized scope</h2>', rendered)
        self.assertIn('<a href="#section-2">1. Login &lt;review&gt;</a>', rendered)
        self.assertIn('<h2 id="section-2">1. Login &lt;review&gt;</h2>', rendered)

    def test_formats_validated_finding_metadata_as_badges(self):
        rendered = markdown_to_html(
            "## Finding\n\n"
            "- Severity: **HIGH**\n"
            "- Status: `needs-review`\n"
            "- Confidence: `medium`\n"
        )
        self.assertIn('<span class="badge severity-high">High</span>', rendered)
        self.assertIn('<span class="badge status-needs-review">Needs-Review</span>', rendered)
        self.assertIn('<span class="badge confidence-medium">Medium</span>', rendered)

    def test_unrecognized_badge_values_remain_escaped_text(self):
        rendered = markdown_to_html("- Severity: **<script>**\n- Status: `<script>`\n")
        self.assertNotIn('<span class="badge severity-', rendered)
        self.assertNotIn('<span class="badge status-', rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)


if __name__ == "__main__":
    unittest.main()
