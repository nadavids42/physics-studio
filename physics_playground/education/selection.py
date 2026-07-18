"""Deterministic audience-depth selection for lesson content."""

from __future__ import annotations

from dataclasses import dataclass

from physics_playground.education.audience import MathematicalDepth, applies_at_depth
from physics_playground.education.models import Lesson, LessonSection, SectionComponent


@dataclass(frozen=True, slots=True)
class SelectedSection:
    section: LessonSection
    components: tuple[SectionComponent, ...]


def select_lesson_sections(lesson: Lesson, depth: MathematicalDepth) -> tuple[SelectedSection, ...]:
    """Select tagged sections and components without changing lesson or physics data."""

    return tuple(
        SelectedSection(
            section,
            tuple(
                component for component in section.components if applies_at_depth(component, depth)
            ),
        )
        for section in lesson.sections
        if applies_at_depth(section, depth)
    )
