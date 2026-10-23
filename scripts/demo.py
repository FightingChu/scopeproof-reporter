"""Build deterministic demo Markdown and HTML reports."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scopeproof.service import compile_report


def main() -> int:
    output = ROOT / "output"
    for output_format, suffix in (("markdown", "md"), ("html", "html")):
        destination = compile_report(
            ROOT / "examples" / "scope.json",
            ROOT / "examples" / "evidence",
            output / f"demo.{suffix}",
            output_format=output_format,
        )
        print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
