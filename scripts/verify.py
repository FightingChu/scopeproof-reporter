"""Complete repository gate for the intentionally incomplete baseline."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def check_batch() -> None:
    path = ROOT / "push_to_remotes.bat"
    raw = path.read_bytes()
    text = raw.decode("gbk")
    if b"\r\n" not in raw or b"\n" in raw.replace(b"\r\n", b""):
        raise SystemExit("push_to_remotes.bat must use CRLF only")
    lowered = text.lower()
    if "chcp 65001" in lowered or "if (" in lowered or "pause" not in lowered:
        raise SystemExit("push script encoding or control-flow contract failed")
    if any(")" in line for line in text.splitlines() if line.lower().startswith("echo ")):
        raise SystemExit("push script echo lines must not contain a right parenthesis")
    if "git@gitee.com:" not in text or "git@github.com:" not in text:
        raise SystemExit("push script must use SSH remotes")
    print("PASS push script GBK CRLF and goto flow")


def main() -> int:
    run("scripts/build.py")
    run("-m", "unittest", "discover", "-s", "tests/unit", "-v")
    run("scripts/demo.py")
    run("scripts/validate_catalog.py")
    run("scripts/check_baseline.py")
    run("scripts/check_docs.py")
    run("scripts/check_scenarios.py")
    run("scripts/count_files.py")
    check_batch()
    print("ALL REPOSITORY GATES PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
