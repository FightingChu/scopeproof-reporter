"""Curated assessment profile loading and rule-family selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .models import ValidationError
from .schema import load_json_objects


@dataclass(frozen=True)
class AssessmentProfile:
    id: str
    title: str
    families: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AssessmentProfile":
        profile_id = data.get("id")
        title = data.get("title")
        families = data.get("families")
        if not isinstance(profile_id, str) or not profile_id.startswith("profile-"):
            raise ValidationError("profile id must start with profile-")
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("profile title must be a non-empty string")
        if not isinstance(families, list) or not families:
            raise ValidationError("profile families must be a non-empty list")
        if any(not isinstance(family, str) or not family.strip() for family in families):
            raise ValidationError("profile families must contain non-empty strings")
        normalized = tuple(family.strip() for family in families)
        if len(set(normalized)) != len(normalized):
            raise ValidationError("profile families must be unique")
        return cls(profile_id, title.strip(), normalized)


class ProfileCatalog:
    def __init__(self, profiles: Iterable[AssessmentProfile], valid_families: Iterable[str]) -> None:
        family_names = set(valid_families)
        by_id: dict[str, AssessmentProfile] = {}
        for profile in profiles:
            if profile.id in by_id:
                raise ValidationError(f"duplicate profile id: {profile.id}")
            unknown = set(profile.families) - family_names
            if unknown:
                raise ValidationError(
                    f"profile {profile.id} references unknown families: {', '.join(sorted(unknown))}"
                )
            by_id[profile.id] = profile
        if not by_id:
            raise ValidationError("profile catalog must contain at least one profile")
        self._profiles = by_id

    @classmethod
    def load(cls, directory: str | Path, valid_families: Iterable[str]) -> "ProfileCatalog":
        parsed: list[AssessmentProfile] = []
        for path, payload in load_json_objects(directory):
            try:
                parsed.append(AssessmentProfile.from_dict(payload))
            except ValidationError as exc:
                raise ValidationError(f"{path}: {exc}") from exc
        return cls(parsed, valid_families)

    def get(self, profile_id: str) -> AssessmentProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise ValidationError(f"unknown profile id: {profile_id}") from exc

    def all(self) -> tuple[AssessmentProfile, ...]:
        return tuple(sorted(self._profiles.values(), key=lambda profile: profile.id))

    def __len__(self) -> int:
        return len(self._profiles)
