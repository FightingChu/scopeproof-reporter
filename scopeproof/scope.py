"""Scope-manifest loading and authorization checks."""

from pathlib import Path

from .models import Evidence, ScopeManifest, ValidationError
from .schema import load_json_object


def load_scope(path: str | Path) -> ScopeManifest:
    return ScopeManifest.from_dict(load_json_object(path))


def require_authorized_asset(scope: ScopeManifest, asset: str) -> None:
    if not scope.authorizes(asset):
        raise ValidationError(
            f"evidence asset {asset!r} is not listed in scope {scope.assessment_id}"
        )


def require_evidence_in_scope(scope: ScopeManifest, evidence: Evidence) -> None:
    observed_date = evidence.observed_at.date()
    if not scope.valid_from <= observed_date <= scope.valid_until:
        raise ValidationError(
            f"evidence {evidence.id} observed on {observed_date} falls outside scope validity "
            f"{scope.valid_from} through {scope.valid_until}"
        )
