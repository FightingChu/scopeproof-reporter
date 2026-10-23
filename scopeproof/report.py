"""Deterministic Markdown report renderer."""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .models import Finding, ScopeManifest
from .redact import redact_text


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def _clean(value: str) -> str:
    return redact_text(value).replace("\r\n", "\n").replace("\r", "\n").strip()


def _render_reproduction(finding: Finding) -> list[str]:
    # Known challenge defect: validated offline steps are currently suppressed.
    return ["### Reproduction", "", "Not included in this report.", ""]


def _render_finding(index: int, finding: Finding) -> list[str]:
    evidence = finding.evidence
    rule = finding.rule
    lines = [
        f"## {index}. {_clean(rule.title)}",
        "",
        f"- Finding ID: `{_clean(evidence.id)}`",
        f"- Rule: `{_clean(rule.id)}`",
        f"- Asset: `{_clean(evidence.asset)}`",
        f"- Severity: **{rule.default_severity.upper()}**",
        f"- Status: `{evidence.status}`",
        f"- Confidence: `{evidence.confidence}`",
        "",
        "### Observation",
        "",
        _clean(evidence.observation),
        "",
        "### Expected control",
        "",
        _clean(rule.expected),
        "",
        "### Impact",
        "",
        _clean(rule.impact),
        "",
        "### Remediation",
        "",
        _clean(rule.remediation),
        "",
    ]
    lines.extend(_render_reproduction(finding))
    if evidence.request or evidence.response:
        lines.extend(["### Evidence excerpts", ""])
        if evidence.request:
            lines.extend(["Request:", "", "```text", _clean(evidence.request), "```", ""])
        if evidence.response:
            lines.extend(["Response:", "", "```text", _clean(evidence.response), "```", ""])
    return lines


def build_markdown(scope: ScopeManifest, findings: Iterable[Finding]) -> str:
    ordered = sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            item.rule.id,
            item.evidence.id,
        ),
    )
    counts = Counter(item.severity for item in ordered)
    lines = [
        "# Internal Security Assessment Report",
        "",
        f"- Assessment: `{_clean(scope.assessment_id)}`",
        f"- Organization: {_clean(scope.organization)}",
        f"- Engagement: {_clean(scope.engagement)}",
        f"- Owner: {_clean(scope.owner)}",
        f"- Validity: `{scope.valid_from.isoformat()}` through `{scope.valid_until.isoformat()}`",
        "",
        "## Authorized scope",
        "",
    ]
    lines.extend(f"- `{_clean(asset)}`" for asset in scope.authorized_assets)
    lines.extend([
        "",
        "## Finding summary",
        "",
        "| Severity | Count |",
        "| --- | ---: |",
    ])
    for severity in ("critical", "high", "medium", "low", "info"):
        lines.append(f"| {severity.title()} | {counts.get(severity, 0)} |")
    lines.extend(["", f"Total findings: **{len(ordered)}**", ""])
    if not ordered:
        lines.extend(["No findings were supplied.", ""])
    for index, finding in enumerate(ordered, start=1):
        lines.extend(_render_finding(index, finding))
    return "\n".join(lines).rstrip() + "\n"
