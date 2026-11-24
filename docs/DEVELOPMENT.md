# Development guide

ScopeProof Reporter supports Python 3.10 and later and uses only the standard library. Run `python scripts/build.py` after source edits and `python -m unittest discover -s tests/unit -v` for behavior checks.

Acceptance files listed in `contracts/immutable.json` are fixed inputs. The repository baseline intentionally keeps S4 failing until the task in `TASK.md` is completed. Expansion work must preserve the exact 5-pass and 1-fail baseline while all unit and repository gates remain green.

Add catalog rules as individual JSON objects. Add profiles only when they select a coherent set of review families. Fixtures must use synthetic assets from reserved example namespaces or loopback addresses.

List supported profiles with `python -m scopeproof profiles` or inspect one with `python -m scopeproof profiles --id profile-browser-application`. Pass `--profile profile-browser-application` to `validate` or `report` to reject evidence whose rule family is outside that profile. Reports record the selected profile.

Use `validate --json` for pipeline integration. Its stable JSON object contains assessment ID, validity, finding counts by severity and rule family, and a sorted list of finding identifiers and classifications. It omits observation text, requests, responses, and evidence summaries.
