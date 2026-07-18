"""Static contract checks for the reusable four-mode experience."""

from physics_playground.presentation.learning_modes import MODE_HELP, LearningMode


def test_all_four_learning_modes_have_help_text() -> None:
    assert tuple(mode.value for mode in LearningMode) == ("Explore", "Compare", "Analyze", "Model")
    assert set(MODE_HELP) == set(LearningMode)
