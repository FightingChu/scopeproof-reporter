# ScopeProof Reporter

ScopeProof Reporter is an offline compiler for internal security assessment reports. It validates an explicit scope manifest, loads already-collected JSON evidence, maps observations to a versioned local rule catalog, redacts common secrets, and produces deterministic Markdown or HTML reports. It never performs discovery, scanning, exploitation, or network requests.

## Quick start

```powershell
python -m scopeproof validate --scope examples/scope.json --evidence examples/evidence
python -m scopeproof report --scope examples/scope.json --evidence examples/evidence --output output/demo.md
python -m scopeproof profiles
python -m scopeproof validate --scope examples/scope.json --evidence examples/evidence/authentication.json --profile profile-browser-application
python -m scopeproof validate --scope examples/scope.json --evidence examples/evidence --json
python scripts/build.py
python -m unittest discover -s tests/unit -v
python tests/run_scenarios.py
```

The challenge described in `TASK.md` intentionally starts with one failing acceptance scenario. Build checks and unit tests must pass before and after the report-template repair. The sealed acceptance baseline is documented in `docs/ACCEPTANCE.md`.

## Repository map

- `scopeproof/`: scope, evidence, catalog, redaction, reporting, and CLI code.
- `catalog/rules/`: one reviewable JSON definition per assessment control.
- `catalog/taxonomies/`: shared field vocabularies used by validators and integrations.
- `profiles/`: curated control selections for common internal assessment types.
- `fixtures/evidence/`: deterministic example observations for parser and report testing.
- `templates/`: Markdown section fragments for downstream customization.
- `tests/scenarios/`: immutable acceptance scenarios.
- `scripts/verify.py`: full repository gate, including expected baseline scenario status.

## Design boundaries

Inputs must name an authorized asset from the scope manifest. Evidence is passive data supplied by the operator and is never executed. Report output is written atomically beneath a caller-selected path. Common bearer tokens, cookies, passwords, API keys, and private-key blocks are removed before rendering.
