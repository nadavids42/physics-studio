from pathlib import Path


def test_magnetic_learning_mode_and_experiment_keys_are_distinct() -> None:
    page = Path(
        "physics_playground/subjects/light_and_electricity/magnetic_forces/page.py"
    ).read_text()
    assert 'mode_navigation(key="magnetic_mode")' in page
    assert 'key=f"{prefix}_experiment"' in page
    assert 'key=f"{prefix}_mode"' not in page
