"""Minimal safe HTML rendering for the deterministic Markdown subset."""

from __future__ import annotations

import html


def markdown_to_html(markdown: str) -> str:
    output = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        "<title>Internal Security Assessment Report</title>",
        "<style>body{font:15px Arial,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#202124}h1,h2,h3{color:#16324f}code,pre{background:#f4f6f8}pre{padding:12px;overflow:auto}table{border-collapse:collapse}th,td{border:1px solid #c7cdd4;padding:6px 10px;text-align:left}th{background:#edf1f5}</style>",
        "</head><body>",
    ]
    in_code = False
    in_list = False
    in_table = False
    for raw_line in markdown.splitlines():
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
            output.append("<tr>" + "".join(f"<{tag}>{html.escape(cell)}</{tag}>" for cell in cells) + "</tr>")
            continue
        if in_table:
            output.append("</table>")
            in_table = False
        if line.startswith("- "):
            if not in_list:
                output.append("<ul>")
                in_list = True
            output.append(f"<li>{html.escape(line[2:])}</li>")
            continue
        if in_list:
            output.append("</ul>")
            in_list = False
        if line.startswith("### "):
            output.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            output.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            output.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line:
            output.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        output.append("</ul>")
    if in_table:
        output.append("</table>")
    if in_code:
        output.append("</pre>")
    output.append("</body></html>")
    return "\n".join(output) + "\n"
