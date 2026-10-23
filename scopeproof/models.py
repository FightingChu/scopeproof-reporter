"""Validated domain models used across the report pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


class ValidationError(ValueError):
    """Raised when a supplied scope, rule, or evidence record is invalid."""


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} must be a non-empty string")
    return value.strip()


def _string_list(data: dict[str, Any], key: str, *, allow_empty: bool = False) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValidationError(f"{key} must be a list of strings")
    cleaned: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"{key} contains an invalid string")
        cleaned.append(item.strip())
    return tuple(cleaned)


@dataclass(frozen=True)
class ScopeManifest:
    assessment_id: str
    organization: str
    engagement: str
    authorized_assets: tuple[str, ...]
    valid_from: date
    valid_until: date
    owner: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScopeManifest":
        try:
            valid_from = date.fromisoformat(_required_text(data, "valid_from"))
            valid_until = date.fromisoformat(_required_text(data, "valid_until"))
        except ValueError as exc:
            raise ValidationError("valid_from and valid_until must be ISO dates") from exc
        if valid_until < valid_from:
            raise ValidationError("valid_until must not precede valid_from")
        assets = _string_list(data, "authorized_assets")
        if len(set(assets)) != len(assets):
            raise ValidationError("authorized_assets must be unique")
        return cls(
            assessment_id=_required_text(data, "assessment_id"),
            organization=_required_text(data, "organization"),
            engagement=_required_text(data, "engagement"),
            authorized_assets=assets,
            valid_from=valid_from,
            valid_until=valid_until,
            owner=_required_text(data, "owner"),
        )

    def authorizes(self, asset: str) -> bool:
        return asset in self.authorized_assets


@dataclass(frozen=True)
class Rule:
    id: str
    family: str
    title: str
    default_severity: str
    summary: str
    expected: str
    impact: str
    remediation: str
    evidence_fields: tuple[str, ...]
    tags: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rule":
        severity = _required_text(data, "default_severity")
        if severity not in {"info", "low", "medium", "high", "critical"}:
            raise ValidationError(f"unsupported severity: {severity}")
        rule_id = _required_text(data, "id")
        if not rule_id.startswith("SP-"):
            raise ValidationError("rule id must start with SP-")
        return cls(
            id=rule_id,
            family=_required_text(data, "family"),
            title=_required_text(data, "title"),
            default_severity=severity,
            summary=_required_text(data, "summary"),
            expected=_required_text(data, "expected"),
            impact=_required_text(data, "impact"),
            remediation=_required_text(data, "remediation"),
            evidence_fields=_string_list(data, "evidence_fields"),
            tags=_string_list(data, "tags"),
        )


@dataclass(frozen=True)
class Evidence:
    id: str
    rule_id: str
    asset: str
    observed_at: datetime
    status: str
    summary: str
    observation: str
    reproduction: tuple[str, ...]
    request: str
    response: str
    confidence: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        status = _required_text(data, "status")
        if status not in {"confirmed", "not-observed", "needs-review"}:
            raise ValidationError(f"unsupported evidence status: {status}")
        confidence = _required_text(data, "confidence")
        if confidence not in {"low", "medium", "high"}:
            raise ValidationError(f"unsupported confidence: {confidence}")
        observed_raw = _required_text(data, "observed_at")
        try:
            observed_at = datetime.fromisoformat(observed_raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationError("observed_at must be an ISO timestamp") from exc
        reproduction = data.get("reproduction", [])
        if not isinstance(reproduction, list) or any(not isinstance(x, str) for x in reproduction):
            raise ValidationError("reproduction must be a list of strings")
        return cls(
            id=_required_text(data, "id"),
            rule_id=_required_text(data, "rule_id"),
            asset=_required_text(data, "asset"),
            observed_at=observed_at,
            status=status,
            summary=_required_text(data, "summary"),
            observation=_required_text(data, "observation"),
            reproduction=tuple(step.strip() for step in reproduction if step.strip()),
            request=str(data.get("request", "")).strip(),
            response=str(data.get("response", "")).strip(),
            confidence=confidence,
        )


@dataclass(frozen=True)
class Finding:
    evidence: Evidence
    rule: Rule

    @property
    def severity(self) -> str:
        return self.rule.default_severity
