import subprocess
import sys
from pathlib import Path

SCENARIO_ID = "S1"
NAME = "build and structure"
ROOT = Path(__file__).resolve().parents[2]


def run(check):
    result = subprocess.run(
        [sys.executable, "scripts/build.py"], cwd=ROOT, text=True, capture_output=True
    )
    check.equal(0, result.returncode, result.stdout + result.stderr)
