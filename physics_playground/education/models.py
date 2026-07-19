"""Typed educational-content contracts independent of Streamlit and renderers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TypeAlias

from physics_playground.education.audience import MathematicalDepth
from physics_playground.models.simulations import LearningMode

ALL_MATHEMATICAL_DEPTHS = frozenset(MathematicalDepth)


class ContentDepth(StrEnum):
    FOUNDATIONAL = "foundational"
    STANDARD = "standard"
    ADVANCED = "advanced"


class ContentVoice(StrEnum):
    APPROACHABLE = "approachable"
    ACADEMIC = "academic"
    CONCISE = "concise"


class PrerequisiteKind(StrEnum):
    CONCEPT = "concept"
    LESSON = "lesson"
    SKILL = "skill"


class ActivityPhase(StrEnum):
    PREDICTION = "prediction"
    EXPLORATION = "exploration"
    COMPARISON = "comparison"
    ANALYSIS = "analysis"
    MODELING = "modeling"
    REFLECTION = "reflection"


class QuestionKind(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_SELECT = "multiple_select"
    NUMERIC = "numeric"
    SHORT_RESPONSE = "short_response"


class EducationEventKind(StrEnum):
    LESSON_STARTED = "lesson_started"
    SECTION_COMPLETED = "section_completed"
    CHECKPOINT_ATTEMPTED = "checkpoint_attempted"
    ACTIVITY_COMPLETED = "activity_completed"
    LESSON_COMPLETED = "lesson_completed"


@dataclass(frozen=True, slots=True)
class ContentProfile:
    """Pedagogical presentation choices, separate from scientific claims."""

    depth: ContentDepth = ContentDepth.STANDARD
    voice: ContentVoice = ContentVoice.APPROACHABLE


@dataclass(frozen=True, slots=True)
class LearningObjective:
    id: str
    statement: str
    evidence: str


@dataclass(frozen=True, slots=True)
class Prerequisite:
    id: str
    kind: PrerequisiteKind
    reference_id: str
    rationale: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class Concept:
    id: str
    name: str
    definition: str
    notation: tuple[str, ...] = ()
    related_concept_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Quantity:
    symbol: str
    name: str
    unit: str


@dataclass(frozen=True, slots=True)
class KnownValue:
    quantity: Quantity
    value: float
    display_value: str | None = None


@dataclass(frozen=True, slots=True)
class ReasoningStep:
    id: str
    expression: str
    explanation: str


@dataclass(frozen=True, slots=True)
class Substitution:
    expression: str
    result: str


@dataclass(frozen=True, slots=True)
class WorkedExample:
    id: str
    title: str
    prompt: str
    known_values: tuple[KnownValue, ...]
    unknown: Quantity
    symbolic_reasoning: tuple[ReasoningStep, ...]
    substitutions: tuple[Substitution, ...]
    unit_check: str
    final_answer: str
    final_interpretation: str
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS


@dataclass(frozen=True, slots=True)
class DerivationStep:
    id: str
    reveal_order: int
    prompt: str
    expression: str
    explanation: str
    hint: str = ""


@dataclass(frozen=True, slots=True)
class GuidedDerivation:
    id: str
    title: str
    goal: str
    assumptions: tuple[str, ...]
    steps: tuple[DerivationStep, ...]
    conclusion: str
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS


@dataclass(frozen=True, slots=True)
class MisconceptionCallout:
    id: str
    misconception: str
    correction: str
    diagnostic_prompt: str = ""
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS


@dataclass(frozen=True, slots=True)
class AnswerChoice:
    id: str
    text: str


@dataclass(frozen=True, slots=True)
class QuestionVariant:
    id: str
    prompt: str
    choices: tuple[AnswerChoice, ...] = ()
    unit_options: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DiagramSpec:
    """Renderer-independent authored diagram reference and nonvisual equivalent."""

    id: str
    asset_id: str
    caption: str
    alt_text: str
    objective_ids: tuple[str, ...]
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "asset_id": self.asset_id,
            "caption": self.caption,
            "alt_text": self.alt_text,
            "objective_ids": list(self.objective_ids),
        }

    @classmethod
    def from_dict(cls, data: object) -> DiagramSpec:
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Unsupported diagram content schema.")
        return cls(
            id=str(data["id"]),
            asset_id=str(data["asset_id"]),
            caption=str(data["caption"]),
            alt_text=str(data["alt_text"]),
            objective_ids=tuple(str(item) for item in data.get("objective_ids", ())),
        )


@dataclass(frozen=True, slots=True)
class CheckpointQuestion:
    id: str
    prompt: str
    kind: QuestionKind
    objective_ids: tuple[str, ...]
    choices: tuple[AnswerChoice, ...] = ()
    unit_options: tuple[str, ...] = ()
    variants: tuple[QuestionVariant, ...] = ()
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        """Serialize only learner-visible content; scoring data lives elsewhere."""

        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "prompt": self.prompt,
            "kind": self.kind.value,
            "objective_ids": list(self.objective_ids),
            "choices": [{"id": choice.id, "text": choice.text} for choice in self.choices],
            "unit_options": list(self.unit_options),
            "variants": [
                {
                    "id": variant.id,
                    "prompt": variant.prompt,
                    "choices": [
                        {"id": choice.id, "text": choice.text} for choice in variant.choices
                    ],
                    "unit_options": list(variant.unit_options),
                }
                for variant in self.variants
            ],
            "applicable_depths": sorted(depth.value for depth in self.applicable_depths),
        }

    @classmethod
    def from_dict(cls, data: object) -> CheckpointQuestion:
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Unsupported checkpoint content schema.")
        choices = data.get("choices", ())
        if not isinstance(choices, list):
            raise ValueError("Checkpoint choices must be a list.")
        return cls(
            id=str(data["id"]),
            prompt=str(data["prompt"]),
            kind=QuestionKind(str(data["kind"])),
            objective_ids=tuple(str(item) for item in data.get("objective_ids", ())),
            choices=tuple(
                AnswerChoice(str(item["id"]), str(item["text"]))
                for item in choices
                if isinstance(item, dict)
            ),
            unit_options=tuple(str(item) for item in data.get("unit_options", ())),
            variants=tuple(
                QuestionVariant(
                    id=str(item["id"]),
                    prompt=str(item["prompt"]),
                    choices=tuple(
                        AnswerChoice(str(choice["id"]), str(choice["text"]))
                        for choice in item.get("choices", ())
                        if isinstance(choice, dict)
                    ),
                    unit_options=tuple(str(unit) for unit in item.get("unit_options", ())),
                )
                for item in data.get("variants", ())
                if isinstance(item, dict)
            ),
            applicable_depths=frozenset(
                MathematicalDepth(str(item)) for item in data.get("applicable_depths", ())
            ),
        )


@dataclass(frozen=True, slots=True)
class SimulationActivity:
    id: str
    phase: ActivityPhase
    simulation_id: str
    title: str
    instructions: tuple[str, ...]
    mode: LearningMode | None = None
    parameter_preset: dict[str, float | int | str | bool] = field(default_factory=dict)
    observation_prompt: str = ""
    completion_evidence: str = ""
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS
    objective_ids: tuple[str, ...] = ()


SectionComponent: TypeAlias = (
    DiagramSpec
    | WorkedExample
    | GuidedDerivation
    | MisconceptionCallout
    | CheckpointQuestion
    | SimulationActivity
)


@dataclass(frozen=True, slots=True)
class LessonSection:
    id: str
    title: str
    narrative: str
    components: tuple[SectionComponent, ...] = ()
    profile: ContentProfile | None = None
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS


@dataclass(frozen=True, slots=True)
class Lesson:
    id: str
    title: str
    summary: str
    objectives: tuple[LearningObjective, ...]
    prerequisites: tuple[Prerequisite, ...]
    concept_ids: tuple[str, ...]
    simulation_ids: tuple[str, ...]
    sections: tuple[LessonSection, ...]
    activity_sequence: tuple[SimulationActivity, ...]
    profile: ContentProfile = ContentProfile()
    estimated_minutes: int = 45
    next_lesson_id: str | None = None
    next_lesson_title: str = ""
    schema_version: int = 1


@dataclass(frozen=True, slots=True)
class Unit:
    id: str
    title: str
    summary: str
    objective_ids: tuple[str, ...]
    lessons: tuple[Lesson, ...]


@dataclass(frozen=True, slots=True)
class Subject:
    id: str
    title: str
    summary: str
    concepts: tuple[Concept, ...]
    units: tuple[Unit, ...]


@dataclass(frozen=True, slots=True)
class CurriculumManifest:
    id: str
    version: str
    title: str
    subjects: tuple[Subject, ...]
    schema_version: int = 1


@dataclass(frozen=True, slots=True)
class EducationProgressEvent:
    id: str
    kind: EducationEventKind
    learner_id: str
    lesson_id: str
    occurred_at: datetime
    section_id: str | None = None
    activity_id: str | None = None
    checkpoint_id: str | None = None
    completed: bool = False
    score: float | None = None
