from physics_playground.education.progress import PathwayProgress
from physics_playground.expansion_catalog import EXPANSION_MANIFESTS
from physics_playground.presentation.navigation import NAVIGATION_SUBJECTS, recommended_lesson
from physics_playground.subjects.mechanics.cannonball.lesson import CANNONBALL_LESSON
from physics_playground.subjects.mechanics.foundations_lesson import MODELS_MEASUREMENTS_LESSON
from physics_playground.subjects.mechanics.kinematics_lessons import KINEMATICS_LESSONS


def test_navigation_catalog_uses_every_validated_simulation_once():
    expected = {manifest.metadata.id for manifest in EXPANSION_MANIFESTS}
    actual = [
        simulation.id for subject in NAVIGATION_SUBJECTS for simulation in subject.simulations
    ]

    assert set(actual) == expected
    assert len(actual) == len(set(actual))


def test_curriculum_lessons_are_joined_to_their_subject_and_recommended_optionally():
    mechanics = next(subject for subject in NAVIGATION_SUBJECTS if subject.id == "mechanics")
    assert CANNONBALL_LESSON in mechanics.lessons
    assert "Motion in two dimensions" in mechanics.units
    assert recommended_lesson({}) == MODELS_MEASUREMENTS_LESSON
    assert (
        recommended_lesson(
            {
                MODELS_MEASUREMENTS_LESSON.id: PathwayProgress(
                    MODELS_MEASUREMENTS_LESSON.id, completed=True
                ),
                CANNONBALL_LESSON.id: PathwayProgress(CANNONBALL_LESSON.id, completed=True),
                **{
                    lesson.id: PathwayProgress(lesson.id, completed=True)
                    for lesson in KINEMATICS_LESSONS
                },
            }
        )
        is None
    )
