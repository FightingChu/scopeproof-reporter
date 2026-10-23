"""Validate rule, taxonomy, profile, and fixture relationships."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scopeproof.catalog import RuleCatalog
from scopeproof.models import Evidence


def read_object(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError(f"expected non-empty object: {path}")
    return payload


def main() -> int:
    catalog = RuleCatalog.load(ROOT / "catalog" / "rules")
    if len(catalog) < 350:
        raise SystemExit(f"expanded catalog requires at least 350 rules, got {len(catalog)}")
    known = {rule.id for rule in catalog.all()}
    distribution = Counter(rule.family for rule in catalog.all())
    if len(distribution) < 12 or min(distribution.values()) < 12:
        raise SystemExit(f"catalog family coverage is too narrow: {dict(distribution)}")

    profiles = sorted((ROOT / "profiles").glob("*.json"))
    for path in profiles:
        profile = read_object(path)
        requested = profile.get("families")
        if not isinstance(requested, list) or len(requested) < 2:
            raise SystemExit(f"profile needs at least two families: {path}")
        unknown = set(requested) - set(distribution)
        if unknown:
            raise SystemExit(f"unknown profile families in {path}: {sorted(unknown)}")

    fixtures = sorted((ROOT / "fixtures" / "evidence").glob("*.json"))
    for path in fixtures:
        evidence = Evidence.from_dict(read_object(path))
        if evidence.rule_id not in known:
            raise SystemExit(f"fixture references unknown rule in {path}: {evidence.rule_id}")

    taxonomies = sorted((ROOT / "catalog" / "taxonomies").glob("*.json"))
    for path in taxonomies:
        payload = read_object(path)
        if not isinstance(payload.get("values"), list) or not payload["values"]:
            raise SystemExit(f"taxonomy has no values: {path}")
    print(
        f"PASS catalog rules={len(catalog)} families={len(distribution)} "
        f"profiles={len(profiles)} fixtures={len(fixtures)} taxonomies={len(taxonomies)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
