"""Definitions describing simulations independently of Streamlit widgets."""

import warnings
from dataclasses import dataclass
from enum import StrEnum


class LearningMode(StrEnum):
    """Canonical modes shared by every current learning experience."""

    EXPLORE = "Explore"
    COMPARE = "Compare"
    ANALYZE = "Analyze"
    MODEL = "Model"


class _LegacySimulationMode(StrEnum):
    """Pre-course mode values retained only for import compatibility."""

    KID = "kid"
    EXPERT = "expert"
    EXPLORE = "Explore"
    COMPARE = "Compare"
    ANALYZE = "Analyze"
    MODEL = "Model"


class Difficulty(StrEnum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


@dataclass(frozen=True, slots=True)
class VisualMetadata:
    accent_color: str
    background: str
    symbol: str
    thumbnail_alt: str


@dataclass(frozen=True, slots=True)
class SimulationDefinition:
    id: str
    title: str
    icon: str
    description: str
    page_module: str
    mission_group: str
    modes: tuple[LearningMode, ...] = tuple(LearningMode)
    central_question: str = "What will happen?"
    concepts: tuple[str, ...] = ()
    difficulty: Difficulty = Difficulty.BEGINNER
    badge_count: int = 0
    renderer: str = "legacy-canvas"
    model_version: str = "legacy"
    simulation_type: str = "Analytical"
    visual: VisualMetadata | None = None

    @property
    def navigation_label(self) -> str:
        return f"{self.icon} {self.title}"


def __getattr__(name: str) -> object:
    """Warn callers that import names superseded by ``LearningMode``."""

    if name == "InteractiveMode":
        warnings.warn(
            "InteractiveMode is deprecated; import LearningMode instead. "
            "The alias will be removed after all supported integrations use LearningMode.",
            DeprecationWarning,
            stacklevel=2,
        )
        return LearningMode
    if name == "SimulationMode":
        warnings.warn(
            "SimulationMode and Kid/Expert modes are deprecated; use LearningMode. "
            "They will be removed when no supported external content imports them.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _LegacySimulationMode
    raise AttributeError(name)
