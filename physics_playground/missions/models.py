"""Typed mission metadata independent of catalog discovery and presentation."""

from dataclasses import dataclass
from enum import StrEnum

from physics_playground.models.simulations import Difficulty


class MissionType(StrEnum):
    DISCOVERY = "Discovery"
    COMPARISON = "Comparison"
    EXPLANATION = "Explanation"


@dataclass(frozen=True, slots=True)
class MissionDefinition:
    id: str
    simulation_id: str
    title: str
    description: str
    hints: tuple[str, ...]
    category: MissionType
    difficulty: Difficulty
    prerequisites: tuple[str, ...]
    hidden: bool
    completion_rule_id: str
    group: str

    @property
    def label(self) -> str:
        return self.title

    @property
    def hint(self) -> str:
        return self.hints[0] if self.hints else ""
