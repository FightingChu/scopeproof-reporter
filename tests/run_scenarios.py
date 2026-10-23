"""Run immutable acceptance scenarios without third-party test dependencies."""

from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@dataclass
class Checks:
    failures: list[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def equal(self, expected, actual, message: str) -> None:
        if expected != actual:
            self.fail(f"{message}: expected={expected!r} actual={actual!r}")

    def contains(self, needle: str, haystack: str, message: str) -> None:
        if needle not in haystack:
            self.fail(message)

    def not_contains(self, needle: str, haystack: str, message: str) -> None:
        if needle in haystack:
            self.fail(message)

    def before(self, first: str, second: str, haystack: str, message: str) -> None:
        left = haystack.find(first)
        right = haystack.find(second)
        if left < 0 or right < 0 or left >= right:
            self.fail(message)


def discover():
    package = importlib.import_module("tests.scenarios")
    names = sorted(
        item.name for item in pkgutil.iter_modules(package.__path__) if item.name.startswith("s")
    )
    return [importlib.import_module(f"tests.scenarios.{name}") for name in names]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    results = []
    for scenario in discover():
        checks = Checks()
        try:
            scenario.run(checks)
        except Exception as exc:
            checks.fail(f"uncaught {type(exc).__name__}: {exc}")
        results.append({
            "id": scenario.SCENARIO_ID,
            "name": scenario.NAME,
            "passed": not checks.failures,
            "failures": checks.failures,
        })
    failed_ids = [result["id"] for result in results if not result["passed"]]
    payload = {
        "passed": len(results) - len(failed_ids),
        "failed": len(failed_ids),
        "failed_ids": failed_ids,
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for result in results:
            print(f"[{'PASS' if result['passed'] else 'FAIL'}] {result['id']} {result['name']}")
            for failure in result["failures"]:
                print(f"  - {failure}")
        print(f"acceptance: {payload['passed']} passed / {payload['failed']} failed")
    return 1 if failed_ids else 0


if __name__ == "__main__":
    raise SystemExit(main())
