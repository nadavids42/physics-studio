"""Validated built-in educational-content catalog."""

from physics_playground.education.models import CurriculumManifest
from physics_playground.education.validation import validate_curriculum_manifest
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.subjects.mechanics.cannonball.lesson import (
    CANNONBALL_ASSESSMENTS,
    MECHANICS_SUBJECT,
)
from physics_playground.subjects.mechanics.foundations_lesson import (
    MODELS_MEASUREMENTS_ASSESSMENTS,
)
from physics_playground.subjects.mechanics.kinematics_lessons import KINEMATICS_ASSESSMENTS

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
ASSESSMENTS = (
    *MODELS_MEASUREMENTS_ASSESSMENTS,
    *KINEMATICS_ASSESSMENTS,
    *CANNONBALL_ASSESSMENTS,
)
ASSESSMENTS_BY_ID = {item.id: item for item in ASSESSMENTS}

validate_curriculum_manifest(
    CURRICULUM,
    simulation_ids={simulation.id for simulation in SIMULATION_REGISTRY},
    assessments=ASSESSMENTS,
)
