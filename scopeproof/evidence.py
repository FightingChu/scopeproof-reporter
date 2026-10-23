"""Offline evidence loading. Evidence content is never executed."""

from pathlib import Path

from .models import Evidence, ValidationError
from .schema import load_json_object


def load_evidence(path: str | Path) -> Evidence:
    return Evidence.from_dict(load_json_object(path))


def load_evidence_path(path: str | Path) -> tuple[Evidence, ...]:
    source = Path(path)
    files = sorted(source.rglob("*.json")) if source.is_dir() else [source]
    if not files:
        raise ValidationError(f"no evidence JSON files found under: {source}")
    records: list[Evidence] = []
    seen: set[str] = set()
    for item in files:
        evidence = load_evidence(item)
        if evidence.id in seen:
            raise ValidationError(f"duplicate evidence id: {evidence.id}")
        seen.add(evidence.id)
        records.append(evidence)
    return tuple(records)
