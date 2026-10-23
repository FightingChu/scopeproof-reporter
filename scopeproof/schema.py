"""Small JSON loading helpers with explicit error messages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ValidationError


def load_json_object(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"file does not exist: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {source}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"top-level JSON value must be an object: {source}")
    return payload


def load_json_objects(directory: str | Path) -> list[tuple[Path, dict[str, Any]]]:
    root = Path(directory)
    if not root.is_dir():
        raise ValidationError(f"directory does not exist: {root}")
    files = sorted(root.rglob("*.json"))
    if not files:
        raise ValidationError(f"no JSON files found under: {root}")
    return [(path, load_json_object(path)) for path in files]
