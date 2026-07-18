import pytest

from physics_playground.canvas.player import build_player_document
from physics_playground.visual.assets import CANVAS_ASSET_JS
from physics_playground.visual.experience import (
    CANVAS_EXPERIENCE_JS, DEFAULT_PRESENTATION_LEVEL, EXPERIENCE_PROFILES, PresentationLevel,
)


def test_three_levels_exist_and_illustrated_is_default():
    assert [level.value for level in PresentationLevel] == ["diagram","illustrated","contextual"]
    assert DEFAULT_PRESENTATION_LEVEL is PresentationLevel.ILLUSTRATED
    assert set(EXPERIENCE_PROFILES) == set(PresentationLevel)


def test_profiles_preserve_scientific_overlays_at_every_level():
    assert all(profile.preserve_scientific_overlays for profile in EXPERIENCE_PROFILES.values())
    assert EXPERIENCE_PROFILES[PresentationLevel.DIAGRAM].depth is False
    assert EXPERIENCE_PROFILES[PresentationLevel.DIAGRAM].environment is False
    assert EXPERIENCE_PROFILES[PresentationLevel.ILLUSTRATED].depth is True
    assert EXPERIENCE_PROFILES[PresentationLevel.ILLUSTRATED].environment is False
    assert EXPERIENCE_PROFILES[PresentationLevel.CONTEXTUAL].environment is True


@pytest.mark.parametrize("level",list(PresentationLevel))
def test_player_accepts_each_explicit_presentation_level(level):
    document=build_player_document(config={"durationMs":1,"tracks":[],"events":[],"presentationLevel":level.value},
        scene_javascript="const scene={draw(){}};",logical_width=100,logical_height=50,
        accessible_label="Experience",idle_hint="Play")
    assert f'"presentationLevel":"{level.value}"' in document
    assert "const PhysicsExperience" in document


def test_shared_assets_remove_depth_in_diagram_mode():
    assert "PhysicsExperience.profile(s).depth" in CANVAS_ASSET_JS
    assert "depth&&o.highlight" in CANVAS_ASSET_JS
    assert "shadow:depth&&" in CANVAS_ASSET_JS


def test_contextual_library_supports_initial_real_world_scenes():
    for context in ("projectileField","laboratory","space","opticsBench","rollerCoaster"):
        assert context in CANVAS_EXPERIENCE_JS
    assert "preserveScientificOverlays:true" in CANVAS_EXPERIENCE_JS
    assert "scientificOverlay" in CANVAS_EXPERIENCE_JS


def test_representative_scenes_opt_into_context_without_hiding_overlays():
    from physics_playground.canvas import cannonball, orbit, pendulum, ray_diagram
    from physics_playground.subjects.mechanics import canvas as mechanics_canvas
    assert "projectileField" in cannonball.SCENE and "for(const track" in cannonball.SCENE
    assert "laboratory" in pendulum.SCENE and "for(const track" in pendulum.SCENE
    assert "space" in orbit.SCENE and "for(const q" in orbit.SCENE
    assert "opticsBench" in ray_diagram.SCENE and "const visible" in ray_diagram.SCENE
    assert "rollerCoaster" in mechanics_canvas.SCENE and "coaster" in mechanics_canvas.SCENE
