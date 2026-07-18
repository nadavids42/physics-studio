"""Presentation-level contracts, preferences, and optional contextual layers."""

from dataclasses import dataclass
from enum import StrEnum

from physics_playground.frontend_assets import load_javascript_asset


class PresentationLevel(StrEnum):
    DIAGRAM = "diagram"
    ILLUSTRATED = "illustrated"
    CONTEXTUAL = "contextual"


class VisualTheme(StrEnum):
    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


DEFAULT_PRESENTATION_LEVEL = PresentationLevel.ILLUSTRATED


@dataclass(frozen=True, slots=True)
class VisualPreferences:
    presentation_level: PresentationLevel = DEFAULT_PRESENTATION_LEVEL
    theme: VisualTheme = VisualTheme.AUTO

    def to_dict(self) -> dict[str, str]:
        return {"presentation_level": self.presentation_level.value, "theme": self.theme.value}

    @classmethod
    def from_dict(cls, data):
        data = data or {}
        try:
            level = PresentationLevel(
                data.get("presentation_level", DEFAULT_PRESENTATION_LEVEL.value)
            )
        except (ValueError, TypeError):
            level = DEFAULT_PRESENTATION_LEVEL
        try:
            theme = VisualTheme(data.get("theme", VisualTheme.AUTO.value))
        except (ValueError, TypeError):
            theme = VisualTheme.AUTO
        return cls(level, theme)


@dataclass(frozen=True, slots=True)
class ExperienceProfile:
    level: PresentationLevel
    depth: bool
    environment: bool
    decorative_detail: bool
    preserve_scientific_overlays: bool = True


EXPERIENCE_PROFILES = {
    PresentationLevel.DIAGRAM: ExperienceProfile(PresentationLevel.DIAGRAM, False, False, False),
    PresentationLevel.ILLUSTRATED: ExperienceProfile(
        PresentationLevel.ILLUSTRATED, True, False, True
    ),
    PresentationLevel.CONTEXTUAL: ExperienceProfile(PresentationLevel.CONTEXTUAL, True, True, True),
}


CANVAS_EXPERIENCE_JS = load_javascript_asset("physics-experience.js")
