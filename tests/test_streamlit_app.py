"""High-value Streamlit application rendering smoke tests."""

from streamlit.testing.v1 import AppTest


def test_app_renders_home_and_a_simulation_page(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PHYSICS_PLAYGROUND_DB", str(tmp_path / "profiles.sqlite3"))
    monkeypatch.setenv("MPLCONFIGDIR", str(tmp_path / "matplotlib"))

    app = AppTest.from_file("app.py").run(timeout=30)
    assert not app.exception
    assert len(app.radio) == 1
    assert "🏠 Mission Control" in app.radio[0].options

    app.radio[0].set_value("cannonball").run(timeout=30)
    assert not app.exception
    assert any(header.value == "🎯 Cannonball Launcher" for header in app.header)
    assert any(button.label == "🔒 Lock in my guess!" for button in app.button)
    assert any(
        expander.label == "Learning pathway: Projectile motion from components"
        for expander in app.expander
    )
