# Reporting workflow

Validate the scope and evidence first, then compile Markdown or HTML. Findings sort by severity, rule ID, and evidence ID so repeated builds are stable. Each finding includes observation, expected control, impact, remediation, reproduction, and optional protocol excerpts.

Markdown is the canonical output. HTML is a self-contained escaped rendering of the supported Markdown subset, with responsive screen layout and A4 print styles. The print stylesheet hides navigation, repeats table headers, and keeps headings, evidence blocks, and finding labels together where possible. Both formats are written through the same atomic local-output helper. Generated reports belong under `output/` or another operator-selected directory and are ignored by Git.
