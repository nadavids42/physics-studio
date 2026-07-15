"""Definitions describing simulations independently of Streamlit widgets."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class SimulationMode(StrEnum):
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
    modes: tuple[SimulationMode, ...] = (SimulationMode.KID,)
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
