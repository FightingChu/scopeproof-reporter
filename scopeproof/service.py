"""Application service for validation and report compilation."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .catalog import RuleCatalog
from .evidence import load_evidence_path
from .io import atomic_write_text
from .models import Finding, ScopeManifest, ValidationError
from .profiles import AssessmentProfile, ProfileCatalog
from .redact import redact_text
from .render_html import markdown_to_html
from .report import SEVERITY_ORDER, build_markdown
from .scope import load_scope, require_authorized_asset, require_evidence_in_scope


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = PROJECT_ROOT / "profiles"


def _attach_evidence_context(markdown: str, findings: tuple[Finding, ...]) -> str:
    ordered = sorted(
        findings,
        key=lambda item: (SEVERITY_ORDER[item.severity], item.rule.id, item.evidence.id),
    )
    cursor = 0
    for index, finding in enumerate(ordered, start=1):
        evidence = finding.evidence
        section_marker = f"\n## {index}. "
        section_start = markdown.find(section_marker, cursor)
        if section_start < 0:
            raise ValidationError(f"generated report is missing finding section {index}")
        section_start += 1

        section_end = markdown.find(f"\n## {index + 1}. ", section_start)
        if section_end < 0:
            section_end = len(markdown)
        finding_id = redact_text(evidence.id).strip()
        marker = f"- Finding ID: `{finding_id}`"
        marker_position = markdown.find(marker, section_start, section_end)
        if marker_position < 0:
            raise ValidationError(f"generated report is missing finding {finding_id}")

        line_end = markdown.find("\n", marker_position, section_end)
        if line_end < 0:
            line_end = section_end
        observed_at = redact_text(evidence.observed_at.isoformat())
        markdown = (
            markdown[:line_end]
            + f"\n- Observed at: `{observed_at}`"
            + markdown[line_end:]
        )

        observation_marker = "### Observation\n\n"
        section_end = markdown.find(f"\n## {index + 1}. ", section_start)
        if section_end < 0:
            section_end = len(markdown)
        observation_position = markdown.find(observation_marker, marker_position, section_end)
        if observation_position < 0:
            raise ValidationError(f"generated report is missing observation section for {finding_id}")

        summary = redact_text(evidence.summary).replace("\r\n", "\n").replace("\r", "\n")
        longest_backtick_run = max(
            (len(match.group(0)) for match in re.finditer(r"`+", summary)),
            default=0,
        )
        fence = "`" * max(3, longest_backtick_run + 1)
        summary_block = (
            f"### Evidence summary\n\n{fence}text\n{summary}\n{fence}"
            "\n\n### Detailed observation\n\n"
        )
        insertion = observation_position + len(observation_marker)
        markdown = markdown[:insertion] + summary_block + markdown[insertion:]
        cursor = section_start
    return markdown


def _attach_family_summary(markdown: str, findings: tuple[Finding, ...]) -> str:
    family_counts = Counter(finding.rule.family for finding in findings)
    if not family_counts:
        return markdown

    total_marker = f"Total findings: **{len(findings)}**\n\n"
    if total_marker not in markdown:
        raise ValidationError("generated report is missing the finding total")

    lines = [
        "## Findings by rule family",
        "",
        "| Rule family | Count |",
        "| --- | ---: |",
    ]
    for family in sorted(family_counts):
        safe_family = redact_text(family).replace("\r", " ").replace("\n", " ")
        safe_family = safe_family.replace("\\", "\\\\").replace("|", "\\|")
        lines.append(f"| {safe_family} | {family_counts[family]} |")
    summary = "\n".join(lines) + "\n\n"
    return markdown.replace(total_marker, total_marker + summary, 1)


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
    markdown = _attach_evidence_context(build_markdown(scope, findings), findings)
    markdown = _attach_family_summary(markdown, findings)
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
