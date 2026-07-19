from dataclasses import replace

import pytest

from physics_playground.education.audience import (
    AUDIENCE_DEFAULTS,
    AudienceLevel,
    AudiencePreferences,
    InstructionalVoice,
    MathematicalDepth,
    VisualDensity,
)
from physics_playground.education.catalog import CURRICULUM
from physics_playground.education.models import (
    GuidedDerivation,
    PrerequisiteKind,
    SimulationActivity,
)
from physics_playground.education.selection import select_lesson_sections
from physics_playground.education.validation import validate_curriculum_manifest
from physics_playground.profiles import LocalProfile, ProfileStore
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.subjects.mechanics.cannonball.lesson import (
    CANNONBALL_ASSESSMENTS,
    CANNONBALL_LESSON,
)
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    simulate_projectile,
)
from physics_playground.validation import PhysicsValidationError


def test_audience_defaults_keep_dimensions_explicit():
    assert AUDIENCE_DEFAULTS[AudienceLevel.EXPLORER] == AudiencePreferences(
        AudienceLevel.EXPLORER,
        InstructionalVoice.CONCRETE,
        MathematicalDepth.CONCEPTUAL,
        VisualDensity.FOCUSED,
    )
    assert AUDIENCE_DEFAULTS[AudienceLevel.CORE] == AudiencePreferences()
    assert (
        AUDIENCE_DEFAULTS[AudienceLevel.ADVANCED].mathematical_depth is MathematicalDepth.EXTENDED
    )


def test_preferences_round_trip_independent_overrides_and_invalid_values():
    preferences = AudiencePreferences(
        AudienceLevel.EXPLORER,
        InstructionalVoice.ACADEMIC,
        MathematicalDepth.STANDARD,
        VisualDensity.DETAILED,
    )
    assert AudiencePreferences.from_dict(preferences.to_dict()) == preferences
    assert AudiencePreferences.from_dict({"audience": "unknown"}) == AudiencePreferences()


def test_cannonball_content_selection_varies_without_lesson_duplication():
    conceptual = select_lesson_sections(CANNONBALL_LESSON, MathematicalDepth.CONCEPTUAL)
    standard = select_lesson_sections(CANNONBALL_LESSON, MathematicalDepth.STANDARD)
    extended = select_lesson_sections(CANNONBALL_LESSON, MathematicalDepth.EXTENDED)

    def components(sections, component_type):
        return [
            item
            for section in sections
            for item in section.components
            if isinstance(item, component_type)
        ]

    assert not components(conceptual, GuidedDerivation)
    assert components(standard, GuidedDerivation)
    assert components(extended, GuidedDerivation)
    assert not any("numerical trajectories" in section.section.title for section in standard)
    assert any("numerical trajectories" in section.section.title for section in extended)
    assert len(components(conceptual, SimulationActivity)) == len(
        CANNONBALL_LESSON.activity_sequence
    )


def test_audience_preferences_cannot_change_projectile_results():
    parameters = ProjectileParameters(launch_speed_m_s=24.0, launch_angle_deg=38.0)
    expected = simulate_projectile(parameters)
    for preferences in AUDIENCE_DEFAULTS.values():
        assert preferences.audience in AudienceLevel
        assert simulate_projectile(parameters) == expected


def test_empty_depth_declaration_is_rejected():
    first_section = replace(CANNONBALL_LESSON.sections[0], applicable_depths=frozenset())
    lesson = replace(CANNONBALL_LESSON, sections=(first_section, *CANNONBALL_LESSON.sections[1:]))
    unit = next(item for item in CURRICULUM.subjects[0].units if CANNONBALL_LESSON in item.lessons)
    subject = CURRICULUM.subjects[0]
    manifest = replace(
        CURRICULUM,
        subjects=(replace(subject, units=(replace(unit, lessons=(lesson,)),)),),
    )
    with pytest.raises(PhysicsValidationError, match="mathematical depth"):
        validate_curriculum_manifest(
            manifest,
            simulation_ids={simulation.id for simulation in SIMULATION_REGISTRY},
            assessments=CANNONBALL_ASSESSMENTS,
        )


def test_pre_audience_content_without_depth_metadata_defaults_to_all_depths():
    source = CANNONBALL_LESSON.sections[0]

    class CompatibilitySection:
        id = source.id
        title = source.title
        narrative = source.narrative
        components = source.components

    lesson = replace(
        CANNONBALL_LESSON,
        sections=(CompatibilitySection(), *CANNONBALL_LESSON.sections[1:]),
        prerequisites=tuple(
            item
            for item in CANNONBALL_LESSON.prerequisites
            if item.kind is not PrerequisiteKind.LESSON
        ),
    )
    unit = next(item for item in CURRICULUM.subjects[0].units if CANNONBALL_LESSON in item.lessons)
    subject = CURRICULUM.subjects[0]
    manifest = replace(
        CURRICULUM,
        subjects=(
            replace(
                subject,
                units=(
                    replace(
                        unit,
                        lessons=(lesson,),
                        objective_ids=tuple(objective.id for objective in lesson.objectives),
                    ),
                ),
            ),
        ),
    )

    validate_curriculum_manifest(
        manifest,
        simulation_ids={simulation.id for simulation in SIMULATION_REGISTRY},
        assessments=CANNONBALL_ASSESSMENTS,
    )
    selected = select_lesson_sections(lesson, MathematicalDepth.CONCEPTUAL)
    assert selected[0].section.id == source.id


def test_instructional_preferences_persist_through_profile_store(tmp_path):
    preferences = AUDIENCE_DEFAULTS[AudienceLevel.ADVANCED]
    store = ProfileStore(tmp_path / "profiles.sqlite3")
    profile = LocalProfile(
        "learner",
        "Learner",
        accessibility_settings={"instructional": preferences.to_dict()},
    )
    store.save(profile)

    restored = store.load(profile.id)
    assert (
        AudiencePreferences.from_dict(restored.accessibility_settings["instructional"])
        == preferences
    )
