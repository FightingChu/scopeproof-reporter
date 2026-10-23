"""Application service for validation and report compilation."""

from __future__ import annotations

from pathlib import Path

from .catalog import RuleCatalog
from .evidence import load_evidence_path
from .io import atomic_write_text
from .models import Finding, ScopeManifest, ValidationError
from .render_html import markdown_to_html
from .report import build_markdown
from .scope import load_scope, require_authorized_asset


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def validate_inputs(
    scope_path: str | Path,
    evidence_path: str | Path,
    catalog_path: str | Path | None = None,
) -> tuple[ScopeManifest, tuple[Finding, ...]]:
    scope = load_scope(scope_path)
    catalog = RuleCatalog.load(catalog_path or PROJECT_ROOT / "catalog" / "rules")
    findings: list[Finding] = []
    for evidence in load_evidence_path(evidence_path):
        require_authorized_asset(scope, evidence.asset)
        rule = catalog.get(evidence.rule_id)
        findings.append(Finding(evidence=evidence, rule=rule))
    return scope, tuple(findings)


def compile_report(
    scope_path: str | Path,
    evidence_path: str | Path,
    output_path: str | Path,
    *,
    output_format: str = "markdown",
    catalog_path: str | Path | None = None,
) -> Path:
    scope, findings = validate_inputs(scope_path, evidence_path, catalog_path)
    markdown = build_markdown(scope, findings)
    if output_format == "markdown":
        content = markdown
    elif output_format == "html":
        content = markdown_to_html(markdown)
    else:
        raise ValidationError(f"unsupported output format: {output_format}")
    return atomic_write_text(output_path, content)
