"""Typed educational-content contracts independent of Streamlit and renderers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TypeAlias

from physics_playground.education.audience import MathematicalDepth
from physics_playground.models.simulations import InteractiveMode

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
class CheckpointQuestion:
    id: str
    prompt: str
    kind: QuestionKind
    objective_ids: tuple[str, ...]
    choices: tuple[AnswerChoice, ...] = ()
    correct_answer: str = ""
    explanation: str = ""
    tolerance: float | None = None
    unit: str = ""
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS


@dataclass(frozen=True, slots=True)
class SimulationActivity:
    id: str
    phase: ActivityPhase
    simulation_id: str
    title: str
    instructions: tuple[str, ...]
    mode: InteractiveMode | None = None
    parameter_preset: dict[str, float | int | str | bool] = field(default_factory=dict)
    observation_prompt: str = ""
    completion_evidence: str = ""
    applicable_depths: frozenset[MathematicalDepth] = ALL_MATHEMATICAL_DEPTHS


SectionComponent: TypeAlias = (
    WorkedExample
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
