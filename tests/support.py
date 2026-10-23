"""Shared deterministic test factories."""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from scopeproof.models import Evidence, Finding, Rule, ScopeManifest

ROOT = Path(__file__).resolve().parents[1]


def scope() -> ScopeManifest:
    return ScopeManifest(
        assessment_id="ASSESS-TEST-001",
        organization="Example Internal Systems",
        engagement="Local report test",
        authorized_assets=("portal.example.test", "127.0.0.1:18080"),
        valid_from=date(2026, 10, 1),
        valid_until=date(2026, 10, 31),
        owner="Internal Security Team",
    )


def rule() -> Rule:
    return Rule(
        id="SP-AUTH-001",
        family="authentication",
        title="Login response account disclosure",
        default_severity="medium",
        summary="Login responses should not disclose account existence.",
        expected="Known and unknown accounts receive equivalent failure responses.",
        impact="An observer can improve account guessing accuracy.",
        remediation="Use one generic response and equivalent processing for failed login attempts.",
        evidence_fields=("request", "response"),
        tags=("login", "enumeration"),
    )


def evidence(*, asset: str = "portal.example.test", reproduction: tuple[str, ...] | None = None) -> Evidence:
    return Evidence(
        id="EV-TEST-001",
        rule_id="SP-AUTH-001",
        asset=asset,
        observed_at=datetime(2026, 10, 10, 10, 30, tzinfo=timezone.utc),
        status="confirmed",
        summary="Synthetic login responses differ.",
        observation="Known and unknown test users receive distinct response text.",
        reproduction=reproduction if reproduction is not None else (
            "curl -i http://127.0.0.1:18080/login -H 'Authorization: Bearer SAMPLE-TOKEN-12345'",
            "Compare the two synthetic responses.",
        ),
        request="Authorization: Bearer SAMPLE-TOKEN-12345",
        response="Set-Cookie: session=SESSION-12345; HttpOnly",
        confidence="high",
    )


def finding(**kwargs) -> Finding:
    return Finding(evidence=evidence(**kwargs), rule=rule())
