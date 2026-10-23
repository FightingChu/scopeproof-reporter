"""Check repository Markdown files and local links."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def main() -> int:
    markdown = sorted(ROOT.rglob("*.md"))
    failures: list[str] = []
    for path in markdown:
        text = path.read_text(encoding="utf-8")
        if not text.strip() or not text.lstrip().startswith("#"):
            failures.append(f"missing heading: {path.relative_to(ROOT)}")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (path.parent / relative).resolve().exists():
                failures.append(f"broken link: {path.relative_to(ROOT)} -> {target}")
    if failures:
        raise SystemExit("documentation check failed:\n" + "\n".join(failures))
    print(f"PASS documentation files={len(markdown)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
