"""Application service for validation and report compilation."""

from __future__ import annotations

from pathlib import Path

from .catalog import RuleCatalog
from .evidence import load_evidence_path
from .io import atomic_write_text
from .models import Finding, ScopeManifest, ValidationError
from .profiles import AssessmentProfile, ProfileCatalog
from .render_html import markdown_to_html
from .report import build_markdown
from .scope import load_scope, require_authorized_asset, require_evidence_in_scope


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = PROJECT_ROOT / "profiles"


def load_profile(profile_id: str, catalog: RuleCatalog | None = None) -> AssessmentProfile:
    rules = catalog or RuleCatalog.load(PROJECT_ROOT / "catalog" / "rules")
    profiles = ProfileCatalog.load(PROFILE_ROOT, rules.families())
    return profiles.get(profile_id)


def validate_inputs(
    scope_path: str | Path,
    evidence_path: str | Path,
    catalog_path: str | Path | None = None,
    profile_id: str | None = None,
) -> tuple[ScopeManifest, tuple[Finding, ...]]:
    scope = load_scope(scope_path)
    catalog = RuleCatalog.load(catalog_path or PROJECT_ROOT / "catalog" / "rules")
    selected_profile = (
        ProfileCatalog.load(PROFILE_ROOT, catalog.families()).get(profile_id)
        if profile_id
        else None
    )
    findings: list[Finding] = []
    for evidence in load_evidence_path(evidence_path):
        require_authorized_asset(scope, evidence.asset)
        require_evidence_in_scope(scope, evidence)
        rule = catalog.get(evidence.rule_id)
        if selected_profile and rule.family not in selected_profile.families:
            raise ValidationError(
                f"rule {rule.id} family {rule.family!r} is outside profile {selected_profile.id}"
            )
        findings.append(Finding(evidence=evidence, rule=rule))
    return scope, tuple(findings)


def compile_report(
    scope_path: str | Path,
    evidence_path: str | Path,
    output_path: str | Path,
    *,
    output_format: str = "markdown",
    catalog_path: str | Path | None = None,
    profile_id: str | None = None,
) -> Path:
    scope, findings = validate_inputs(scope_path, evidence_path, catalog_path, profile_id)
    markdown = build_markdown(scope, findings)
    if profile_id:
        profile = load_profile(profile_id)
        markdown = markdown.replace(
            "## Authorized scope\n",
            f"- Assessment profile: `{profile.title}` (`{profile.id}`)\n\n## Authorized scope\n",
            1,
        )
    if output_format == "markdown":
        content = markdown
    elif output_format == "html":
        content = markdown_to_html(markdown)
    else:
        raise ValidationError(f"unsupported output format: {output_format}")
    return atomic_write_text(output_path, content)
