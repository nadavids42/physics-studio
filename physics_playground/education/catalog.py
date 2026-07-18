"""Validated built-in educational-content catalog."""

from physics_playground.education.lessons.cannonball import MECHANICS_SUBJECT
from physics_playground.education.models import CurriculumManifest
from physics_playground.education.validation import validate_curriculum_manifest
from physics_playground.registry import SIMULATION_REGISTRY

CURRICULUM = CurriculumManifest(
    id="physics-studio-core",
    version="1.0",
    title="Physics Studio interactive textbook",
    subjects=(MECHANICS_SUBJECT,),
)

LESSONS_BY_ID = {
    lesson.id: lesson
    for subject in CURRICULUM.subjects
    for unit in subject.units
    for lesson in unit.lessons
}

validate_curriculum_manifest(
    CURRICULUM, simulation_ids={simulation.id for simulation in SIMULATION_REGISTRY}
)
