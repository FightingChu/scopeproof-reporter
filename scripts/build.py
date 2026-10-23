"""Syntax and structural build gate."""

from __future__ import annotations

import compileall
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scopeproof.catalog import RuleCatalog
from scopeproof.scope import load_scope


def main() -> int:
    for directory in (ROOT / "scopeproof", ROOT / "scripts", ROOT / "tests"):
        if not compileall.compile_dir(directory, quiet=1, force=True):
            raise SystemExit(f"syntax compilation failed under {directory}")
    scope = load_scope(ROOT / "examples" / "scope.json")
    catalog = RuleCatalog.load(ROOT / "catalog" / "rules")
    if len(catalog) < 2:
        raise SystemExit("catalog must contain at least two seed rules")
    for path in sorted((ROOT / "config").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not payload:
            raise SystemExit(f"invalid non-object config: {path}")
    print(
        f"PASS build assessment={scope.assessment_id} "
        f"rules={len(catalog)} families={len(catalog.families())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
