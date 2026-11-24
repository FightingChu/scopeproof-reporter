"""Minimal safe HTML rendering for the deterministic Markdown subset."""

from __future__ import annotations

import html
import re


SEVERITIES = {"critical", "high", "medium", "low", "info"}
STATUSES = {"confirmed", "not-observed", "needs-review"}
CONFIDENCES = {"high", "medium", "low"}
REPORT_STYLES = (
    "<style>"
    "body{font:15px Arial,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#202124;background:#f7f9fb}"
    "main{background:#fff;padding:clamp(1rem,4vw,2.5rem);border:1px solid #dce2e8;border-radius:12px}"
    "h1,h2,h3{color:#16324f}h2{scroll-margin-top:1rem}a{color:#1359a6}"
    ".report-toc{padding:1rem 1.25rem;margin:1.5rem 0;background:#f0f4f8;border:1px solid #dce4ec;border-radius:8px}"
    ".report-toc h2{margin-top:0}.report-toc ul{margin-bottom:0;padding-left:1.2rem}.report-toc li{margin:.35rem 0}"
    "code,pre{background:#f4f6f8}pre{padding:12px;overflow:auto;border:1px solid #e2e7ed;border-radius:6px}"
    "table{border-collapse:collapse}th,td{border:1px solid #c7cdd4;padding:6px 10px;text-align:left}th{background:#edf1f5}"
    ".badge{display:inline-block;padding:.18rem .55rem;border-radius:999px;font-size:.82rem;font-weight:700;white-space:nowrap}"
    ".severity-critical,.severity-high{color:#842029;background:#f8d7da}.severity-medium{color:#664d03;background:#fff3cd}"
    ".severity-low,.severity-info{color:#084298;background:#cfe2ff}.status-confirmed{color:#146c43;background:#d1e7dd}"
    ".status-not-observed{color:#495057;background:#e2e3e5}.status-needs-review{color:#664d03;background:#fff3cd}"
    ".confidence-high{color:#146c43;background:#d1e7dd}.confidence-medium{color:#664d03;background:#fff3cd}"
    ".confidence-low{color:#495057;background:#e2e3e5}li{margin:.2rem 0}p{line-height:1.55}"
    "@page{size:A4;margin:18mm 16mm}"
    "@media print{body{max-width:none;margin:0;padding:0;background:#fff;color:#111;font-size:10pt}"
    "main{padding:0;border:0;border-radius:0}.report-toc{display:none}"
    "h1,h2,h3{color:#111;break-after:avoid-page}h2{margin-top:1.2em}"
    "a{color:inherit;text-decoration:none}a[href^='#']{color:inherit}"
    "pre,table,tr,.badge{break-inside:avoid-page}pre{white-space:pre-wrap;overflow-wrap:anywhere}"
    "thead{display:table-header-group}tfoot{display:table-footer-group}"
    ".severity-critical,.severity-high,.severity-medium,.severity-low,.severity-info,"
    ".status-confirmed,.status-not-observed,.status-needs-review,.confidence-high,.confidence-medium,.confidence-low{"
    "color:#111;background:#fff;border:1px solid #777}"
    "}"
    "</style>"
)


def _metadata_badge(item: str) -> str | None:
    severity = re.fullmatch(r"Severity: \*\*(critical|high|medium|low|info)\*\*", item, re.IGNORECASE)
    if severity:
        value = severity.group(1).lower()
        return f'Severity: <span class="badge severity-{value}">{value.title()}</span>'
    status = re.fullmatch(r"Status: `([^`]+)`", item)
    if status and status.group(1) in STATUSES:
        value = status.group(1)
        return f'Status: <span class="badge status-{value}">{value.title()}</span>'
    confidence = re.fullmatch(r"Confidence: `([^`]+)`", item)
    if confidence and confidence.group(1) in CONFIDENCES:
        value = confidence.group(1)
        return f'Confidence: <span class="badge confidence-{value}">{value.title()}</span>'
    return None


def _toc(markdown_lines: list[str]) -> tuple[list[str], dict[int, str]]:
    headings = [
        (line_number, line[3:].strip())
        for line_number, line in enumerate(markdown_lines)
        if line.startswith("## ")
    ]
    anchors = {
        line_number: f"section-{index}"
        for index, (line_number, _) in enumerate(headings, start=1)
    }
    output = [
        '<nav class="report-toc" aria-label="Report contents">',
        "<h2>Contents</h2>",
        "<ul>",
    ]
    for line_number, title in headings:
        output.append(f'<li><a href="#{anchors[line_number]}">{_inline(title)}</a></li>')
    output.extend(["</ul>", "</nav>"])
    return output, anchors


def _inline(markdown_text: str) -> str:
    parts = re.split(r"(`[^`]*`|\*\*[^*]+\*\*|(?<!\*)\*[^*\n]+\*(?!\*))", markdown_text)
    output: list[str] = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            output.append(f"<code>{html.escape(part[1:-1])}</code>")
        elif part.startswith("**") and part.endswith("**"):
            output.append(f"<strong>{html.escape(part[2:-2])}</strong>")
        elif part.startswith("*") and part.endswith("*"):
            output.append(f"<em>{html.escape(part[1:-1])}</em>")
        else:
            output.append(html.escape(part))
    return "".join(output)


def markdown_to_html(markdown: str) -> str:
    markdown_lines = markdown.splitlines()
    toc, anchors = _toc(markdown_lines)
    output = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Internal Security Assessment Report</title>",
        REPORT_STYLES,
        "</head><body>",
        "<main>",
    ]
    output.extend(toc)
    in_code = False
    in_list = False
    in_table = False
    for line_number, raw_line in enumerate(markdown_lines):
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append("</pre>" if in_code else "<pre>")
            in_code = not in_code
            continue
        if in_code:
            output.append(html.escape(line) + "\n")
            continue
        if line.startswith("| ") and line.endswith(" |"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(set(cell) <= {"-", ":"} for cell in cells):
                continue
            if not in_table:
                output.append("<table>")
                in_table = True
            tag = "th" if cells[0] == "Severity" else "td"
            output.append("<tr>" + "".join(f"<{tag}>{_inline(cell)}</{tag}>" for cell in cells) + "</tr>")
            continue
        if in_table:
            output.append("</table>")
            in_table = False
        if line.startswith("- "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            item = line[2:]
            badge = _metadata_badge(item)
            output.append(f"<li>{badge if badge is not None else _inline(item)}</li>")
            continue
        if in_list:
            output.append("</ul>")
            in_list = False
        if line.startswith("### "):
            output.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            anchor = anchors[line_number]
            output.append(f'<h2 id="{anchor}">{_inline(line[3:])}</h2>')
        elif line.startswith("# "):
            output.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line:
            output.append(f"<p>{_inline(line)}</p>")
    if in_list:
        output.append("</ul>")
    if in_table:
        output.append("</table>")
    if in_code:
        output.append("</pre>")
    output.extend(["</main>", "</body></html>"])
    return "\n".join(output) + "\n"
