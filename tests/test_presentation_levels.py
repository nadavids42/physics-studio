from physics_playground.visual.experience import (
    DEFAULT_PRESENTATION_LEVEL,
    EXPERIENCE_PROFILES,
    PresentationLevel,
)


def test_three_levels_exist_and_illustrated_is_default():
    assert [level.value for level in PresentationLevel] == ["diagram", "illustrated", "contextual"]
    assert DEFAULT_PRESENTATION_LEVEL is PresentationLevel.ILLUSTRATED
    assert set(EXPERIENCE_PROFILES) == set(PresentationLevel)


def test_profiles_preserve_scientific_overlays_at_every_level():
    assert all(profile.preserve_scientific_overlays for profile in EXPERIENCE_PROFILES.values())
    assert EXPERIENCE_PROFILES[PresentationLevel.DIAGRAM].depth is False
    assert EXPERIENCE_PROFILES[PresentationLevel.DIAGRAM].environment is False
    assert EXPERIENCE_PROFILES[PresentationLevel.ILLUSTRATED].depth is True
    assert EXPERIENCE_PROFILES[PresentationLevel.ILLUSTRATED].environment is False
    assert EXPERIENCE_PROFILES[PresentationLevel.CONTEXTUAL].environment is True
