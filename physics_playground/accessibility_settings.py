"""Shared accessibility preferences and rendering utilities."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from physics_playground.education.audience import AudiencePreferences


@dataclass(frozen=True, slots=True)
class AccessibilitySettings:
    reduced_motion: bool = False
    high_contrast: bool = False
    large_text: bool = False
    instructional: AudiencePreferences = AudiencePreferences()

    def to_dict(self) -> dict[str, object]:
        return {
            "reduced_motion": self.reduced_motion,
            "high_contrast": self.high_contrast,
            "large_text": self.large_text,
            "instructional": self.instructional.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> AccessibilitySettings:
        return cls(
            bool(data.get("reduced_motion", False)),
            bool(data.get("high_contrast", False)),
            bool(data.get("large_text", False)),
            AudiencePreferences.from_dict(data.get("instructional")),
        )
