"""Command-line interface for offline validation and report rendering."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import RuleCatalog
from .models import ValidationError
from .service import PROJECT_ROOT, compile_report, validate_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scopeproof")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate scope and offline evidence")
    validate.add_argument("--scope", required=True)
    validate.add_argument("--evidence", required=True)
    validate.add_argument("--catalog", default=str(PROJECT_ROOT / "catalog" / "rules"))

    report = subparsers.add_parser("report", help="compile a local assessment report")
    report.add_argument("--scope", required=True)
    report.add_argument("--evidence", required=True)
    report.add_argument("--output", required=True)
    report.add_argument("--format", choices=("markdown", "html"), default="markdown")
    report.add_argument("--catalog", default=str(PROJECT_ROOT / "catalog" / "rules"))

    catalog = subparsers.add_parser("catalog", help="summarize the local control catalog")
    catalog.add_argument("--path", default=str(PROJECT_ROOT / "catalog" / "rules"))
    catalog.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            scope, findings = validate_inputs(args.scope, args.evidence, args.catalog)
            print(f"valid assessment={scope.assessment_id} evidence={len(findings)}")
            return 0
        if args.command == "report":
            destination = compile_report(
                args.scope,
                args.evidence,
                args.output,
                output_format=args.format,
                catalog_path=args.catalog,
            )
            print(destination)
            return 0
        loaded = RuleCatalog.load(args.path)
        payload = {"rules": len(loaded), "families": list(loaded.families())}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"rules={payload['rules']} families={len(payload['families'])}")
        return 0
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
