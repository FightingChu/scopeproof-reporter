"""Versioned local assessment-rule catalog."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import Rule, ValidationError
from .schema import load_json_objects


class RuleCatalog:
    def __init__(self, rules: Iterable[Rule]) -> None:
        by_id: dict[str, Rule] = {}
        for rule in rules:
            if rule.id in by_id:
                raise ValidationError(f"duplicate rule id: {rule.id}")
            by_id[rule.id] = rule
        if not by_id:
            raise ValidationError("catalog must contain at least one rule")
        self._rules = by_id

    @classmethod
    def load(cls, directory: str | Path) -> "RuleCatalog":
        parsed: list[Rule] = []
        for path, payload in load_json_objects(directory):
            try:
                parsed.append(Rule.from_dict(payload))
            except ValidationError as exc:
                raise ValidationError(f"{path}: {exc}") from exc
        return cls(parsed)

    def get(self, rule_id: str) -> Rule:
        try:
            return self._rules[rule_id]
        except KeyError as exc:
            raise ValidationError(f"unknown rule id: {rule_id}") from exc

    def all(self) -> tuple[Rule, ...]:
        return tuple(sorted(self._rules.values(), key=lambda item: item.id))

    def families(self) -> tuple[str, ...]:
        return tuple(sorted({rule.family for rule in self._rules.values()}))

    def __len__(self) -> int:
        return len(self._rules)
