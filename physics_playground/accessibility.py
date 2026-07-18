"""Shared accessibility preferences and rendering utilities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class AccessibilitySettings:
    reduced_motion: bool = False
    high_contrast: bool = False
    large_text: bool = False

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> AccessibilitySettings:
        return cls(
            bool(data.get("reduced_motion", False)),
            bool(data.get("high_contrast", False)),
            bool(data.get("large_text", False)),
        )
