# Rule catalog

Each file under `catalog/rules` contains one reporting control. A rule defines its stable ID, family, title, default severity, review expectation, impact statement, remediation guidance, required evidence fields, and search tags.

Rule IDs use `SP-<FAMILY>-<NUMBER>`. IDs are immutable once evidence refers to them. Wording can be clarified in a versioned change, but a material change to the control expectation requires a new ID. `scripts/validate_catalog.py` rejects duplicate IDs, unknown profile families, orphan fixtures, and insufficient family coverage.

Rules guide evidence review; they do not send traffic or infer a finding from raw targets. Operators decide the evidence status and retain the supporting request and response as inert report input.
