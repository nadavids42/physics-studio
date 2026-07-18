"""Registry- and curriculum-backed navigation models for the application shell."""

from __future__ import annotations

from dataclasses import dataclass

from physics_playground.education.catalog import CURRICULUM
from physics_playground.education.models import Lesson
from physics_playground.expansion_catalog import EXPANSION_MANIFESTS
from physics_playground.models.expansion import SubjectArea
from physics_playground.models.simulations import SimulationDefinition

SUBJECT_TITLES = {
    SubjectArea.MECHANICS: "Mechanics",
    SubjectArea.WAVES_AND_OSCILLATIONS: "Waves and oscillations",
    SubjectArea.LIGHT_AND_ELECTRICITY: "Light and electricity",
    SubjectArea.FLUIDS_AND_MATTER: "Fluids and matter",
}


@dataclass(frozen=True, slots=True)
class NavigationSubject:
    id: str
    title: str
    simulations: tuple[SimulationDefinition, ...]
    lessons: tuple[Lesson, ...] = ()
    units: tuple[str, ...] = ()

    @property
    def concepts(self) -> tuple[str, ...]:
        return tuple(sorted({concept for item in self.simulations for concept in item.concepts}))


def build_navigation_subjects() -> tuple[NavigationSubject, ...]:
    """Join validated expansion and curriculum metadata without duplicating it."""

    curriculum_subjects = {subject.id: subject for subject in CURRICULUM.subjects}
    subjects = []
    for area in SubjectArea:
        simulations = tuple(
            manifest.metadata for manifest in EXPANSION_MANIFESTS if manifest.subject is area
        )
        curriculum = curriculum_subjects.get(area.value)
        lessons = (
            tuple(lesson for unit in curriculum.units for lesson in unit.lessons)
            if curriculum
            else ()
        )
        units = tuple(unit.title for unit in curriculum.units) if curriculum else ()
        subjects.append(
            NavigationSubject(
                area.value,
                curriculum.title if curriculum else SUBJECT_TITLES[area],
                simulations,
                lessons,
                units,
            )
        )
    return tuple(subjects)


NAVIGATION_SUBJECTS = build_navigation_subjects()
SUBJECTS_BY_ID = {subject.id: subject for subject in NAVIGATION_SUBJECTS}


def recommended_lesson(progress: object) -> Lesson | None:
    """Return the first unfinished lesson; recommendations never gate other content."""

    progress_by_lesson = progress if isinstance(progress, dict) else {}
    for subject in NAVIGATION_SUBJECTS:
        for lesson in subject.lessons:
            item = progress_by_lesson.get(lesson.id)
            if not bool(getattr(item, "completed", False)):
                return lesson
    return None
