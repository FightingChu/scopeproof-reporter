# Architecture

ScopeProof Reporter has a one-way pipeline: scope manifest and offline evidence enter validation, rules add reporting context, redaction removes common credentials, and a renderer produces local text. The package has no HTTP client, socket use, subprocess calls, plug-in loader, or dynamic expression evaluation.

`ScopeManifest` owns the asset allowlist and validity dates. `Evidence` owns observations and reproduction text as inert strings. `RuleCatalog` loads reviewable JSON controls. `service.validate_inputs` joins evidence to rules only after checking scope. `report.build_markdown` and `render_html.markdown_to_html` produce deterministic output. `io.atomic_write_text` replaces the destination only after a complete temporary file has been flushed.

The catalog is data rather than executable code. Profiles select families for a review workflow but do not alter rule content. Taxonomies document shared vocabulary. Fixtures remain synthetic and use loopback or reserved example names.
