"""Audience and instructional-presentation preferences."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, TypeVar


class AudienceLevel(StrEnum):
    EXPLORER = "explorer"
    CORE = "core"
    ADVANCED = "advanced"


class InstructionalVoice(StrEnum):
    CONCRETE = "concrete"
    APPROACHABLE = "approachable"
    ACADEMIC = "academic"


class MathematicalDepth(StrEnum):
    CONCEPTUAL = "conceptual"
    STANDARD = "standard"
    EXTENDED = "extended"


class VisualDensity(StrEnum):
    FOCUSED = "focused"
    BALANCED = "balanced"
    DETAILED = "detailed"


@dataclass(frozen=True, slots=True)
class AudiencePreferences:
    audience: AudienceLevel = AudienceLevel.CORE
    voice: InstructionalVoice = InstructionalVoice.APPROACHABLE
    mathematical_depth: MathematicalDepth = MathematicalDepth.STANDARD
    visual_density: VisualDensity = VisualDensity.BALANCED

    def to_dict(self) -> dict[str, str]:
        return {
            "audience": self.audience.value,
            "voice": self.voice.value,
            "mathematical_depth": self.mathematical_depth.value,
            "visual_density": self.visual_density.value,
        }

    @classmethod
    def from_dict(cls, data: object) -> AudiencePreferences:
        if not isinstance(data, dict):
            return cls()
        defaults = cls()

        enum_value = TypeVar("enum_value", bound=StrEnum)

        def parse(enum_type: type[enum_value], key: str, fallback: enum_value) -> enum_value:
            raw = data.get(key, fallback.value)
            if not isinstance(raw, str):
                return fallback
            try:
                return enum_type(raw)
            except ValueError:
                return fallback

        return cls(
            parse(AudienceLevel, "audience", defaults.audience),
            parse(InstructionalVoice, "voice", defaults.voice),
            parse(MathematicalDepth, "mathematical_depth", defaults.mathematical_depth),
            parse(VisualDensity, "visual_density", defaults.visual_density),
        )


AUDIENCE_DEFAULTS = {
    AudienceLevel.EXPLORER: AudiencePreferences(
        AudienceLevel.EXPLORER,
        InstructionalVoice.CONCRETE,
        MathematicalDepth.CONCEPTUAL,
        VisualDensity.FOCUSED,
    ),
    AudienceLevel.CORE: AudiencePreferences(),
    AudienceLevel.ADVANCED: AudiencePreferences(
        AudienceLevel.ADVANCED,
        InstructionalVoice.ACADEMIC,
        MathematicalDepth.EXTENDED,
        VisualDensity.DETAILED,
    ),
}


class DepthTagged(Protocol):
    @property
    def applicable_depths(self) -> frozenset[MathematicalDepth]: ...


def applies_at_depth(block: DepthTagged, depth: MathematicalDepth) -> bool:
    """Return whether a tagged content block applies at the selected depth."""

    return depth in block.applicable_depths
