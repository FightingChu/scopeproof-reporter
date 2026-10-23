# Internal assessment report template task

The security team uses this repository to compile an authorized internal penetration-test report from offline evidence. No command in the evidence is executed and the application has no network client.

Complete the reproduction section in `scopeproof/report.py` so each confirmed finding includes the supplied, validated reproduction steps in a fenced text block. Preserve input order, redact secrets with the existing `redact_text` helper, and render an explicit `Not provided` line when the evidence has no steps.

Delivery requirements:

1. `python scripts/build.py` passes.
2. `python -m unittest discover -s tests/unit -v` passes.
3. `python tests/run_scenarios.py` reports S1-S6 passing.
4. Do not modify `TASK.md`, `docs/ACCEPTANCE.md`, `tests/run_scenarios.py`, or anything under `tests/scenarios/`; they are the acceptance baseline.
5. Do not add network access, command execution, or third-party dependencies.
