"""Validate the tracked effective-file budget."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item)


def main() -> int:
    files = tracked_files()
    if not 500 <= len(files) <= 520:
        raise SystemExit(f"tracked file count must be 500-520, got {len(files)}")
    empty = [name for name in files if not (ROOT / name).read_bytes().strip()]
    if empty:
        raise SystemExit("empty tracked files: " + ", ".join(empty))
    print(f"PASS tracked effective files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
