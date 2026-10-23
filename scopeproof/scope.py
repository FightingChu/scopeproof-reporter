"""Scope-manifest loading and authorization checks."""

from pathlib import Path

from .models import ScopeManifest, ValidationError
from .schema import load_json_object


def load_scope(path: str | Path) -> ScopeManifest:
    return ScopeManifest.from_dict(load_json_object(path))


def require_authorized_asset(scope: ScopeManifest, asset: str) -> None:
    if not scope.authorizes(asset):
        raise ValidationError(
            f"evidence asset {asset!r} is not listed in scope {scope.assessment_id}"
        )
