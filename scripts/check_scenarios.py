"""Assert the intentionally incomplete baseline scenario result."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    result = subprocess.run(
        [sys.executable, "tests/run_scenarios.py", "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    passed = payload.get("passed")
    failed = payload.get("failed")
    failed_ids = payload.get("failed_ids")
    if result.returncode != 1 or passed != 5 or failed != 1 or failed_ids != ["S4"]:
        raise SystemExit(
            "baseline scenarios changed: "
            f"returncode={result.returncode} payload={payload} stderr={result.stderr!r}"
        )
    print("PASS baseline scenarios=5 passed/1 expected failure S4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
