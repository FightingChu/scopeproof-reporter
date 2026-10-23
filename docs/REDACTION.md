# Redaction rules

Report rendering removes common bearer values, cookie headers, password-like assignments, API keys, access and refresh tokens, generic secret assignments, and PEM private-key blocks. Labels and header names remain visible so a reviewer understands what was removed.

Redaction is deterministic and occurs before Markdown or HTML rendering. Inputs should still be collected with the least sensitive detail needed for review. Synthetic fixtures use reserved hosts and placeholder credentials to exercise the same path without carrying real secrets.
