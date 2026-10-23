# Acceptance scenarios

These scenarios are the immutable delivery baseline for the internal assessment report task.

## S1 - Build and structure

`python scripts/build.py` must compile all Python sources and validate the seed catalog, configuration, and example scope.

## S2 - Scope enforcement

Evidence for an asset not listed in `authorized_assets` must be rejected before report construction.

## S3 - Finding summary

Markdown output must contain the assessment identity, authorized assets, deterministic severity counts, and each supplied finding.

## S4 - Reproduction section

A confirmed finding must preserve its supplied reproduction steps in input order inside a fenced text block. Secret values must pass through the existing redaction helper. Empty steps must render `Not provided`.

## S5 - Secret redaction

Bearer tokens, cookies, passwords, API keys, access tokens, refresh tokens, generic secrets, and private-key blocks must not appear in a generated report.

## S6 - Atomic local output

Markdown and HTML output must be written atomically to the requested local path. The report compiler must not execute evidence text or make network requests.
