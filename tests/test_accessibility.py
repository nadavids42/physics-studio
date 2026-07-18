from physics_playground.accessibility import AccessibilitySettings
from physics_playground.profiles import LocalProfile


def test_accessibility_settings_round_trip():
    settings = AccessibilitySettings(reduced_motion=True, high_contrast=True, large_text=True)
    assert AccessibilitySettings.from_dict(settings.to_dict()) == settings


def test_profile_preserves_accessibility_preferences():
    profile = LocalProfile.from_dict(
        {
            "id": "p",
            "display_name": "Scientist",
            "accessibility_settings": {
                "reduced_motion": True,
                "high_contrast": True,
                "large_text": False,
            },
        }
    )
    assert profile.accessibility_settings["reduced_motion"] is True
    assert profile.accessibility_settings["high_contrast"] is True
