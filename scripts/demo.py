"""Build deterministic demo Markdown and HTML reports."""

from pathlib import Path

from scopeproof.service import compile_report

ROOT = Path(__file__).resolve().parents[1]


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
