"""Command-line interface for offline validation and report rendering."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalog import RuleCatalog
from .models import ValidationError
from .profiles import ProfileCatalog
from .service import PROFILE_ROOT, PROJECT_ROOT, compile_report, load_profile, validate_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scopeproof")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate scope and offline evidence")
    validate.add_argument("--scope", required=True)
    validate.add_argument("--evidence", required=True)
    validate.add_argument("--catalog", default=str(PROJECT_ROOT / "catalog" / "rules"))
    validate.add_argument("--profile", help="restrict evidence to a curated local profile")

    report = subparsers.add_parser("report", help="compile a local assessment report")
    report.add_argument("--scope", required=True)
    report.add_argument("--evidence", required=True)
    report.add_argument("--output", required=True)
    report.add_argument("--format", choices=("markdown", "html"), default="markdown")
    report.add_argument("--catalog", default=str(PROJECT_ROOT / "catalog" / "rules"))
    report.add_argument("--profile", help="apply a curated local profile")

    profiles = subparsers.add_parser("profiles", help="list or inspect curated local profiles")
    profiles.add_argument("--id", help="show one profile and its selected families")
    profiles.add_argument("--catalog", default=str(PROJECT_ROOT / "catalog" / "rules"))

    catalog = subparsers.add_parser("catalog", help="summarize the local control catalog")
    catalog.add_argument("--path", default=str(PROJECT_ROOT / "catalog" / "rules"))
    catalog.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate":
            scope, findings = validate_inputs(args.scope, args.evidence, args.catalog, args.profile)
            print(f"valid assessment={scope.assessment_id} evidence={len(findings)}")
            return 0
        if args.command == "report":
            destination = compile_report(
                args.scope,
                args.evidence,
                args.output,
                output_format=args.format,
                catalog_path=args.catalog,
                profile_id=args.profile,
            )
            print(destination)
            return 0
        if args.command == "profiles":
            catalog = RuleCatalog.load(args.catalog)
            if args.id:
                profile = load_profile(args.id, catalog)
                payload = {"id": profile.id, "title": profile.title, "families": list(profile.families)}
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                profiles = ProfileCatalog.load(PROFILE_ROOT, catalog.families())
                payload = [
                    {"id": profile.id, "title": profile.title, "families": len(profile.families)}
                    for profile in profiles.all()
                ]
                print(json.dumps(payload, ensure_ascii=False, indent=2))
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
