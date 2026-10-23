"""Verify hashes for immutable task and acceptance files."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest_path = ROOT / "contracts" / "immutable.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = []
    for relative, expected in sorted(manifest.items()):
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"missing {relative}")
        elif digest(path) != expected:
            failures.append(f"changed {relative}")
    if failures:
        raise SystemExit("immutable baseline failure: " + "; ".join(failures))
    print(f"PASS immutable baseline files={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
