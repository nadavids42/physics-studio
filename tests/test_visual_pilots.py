import matplotlib.pyplot as plt

from physics_playground.presentation.chart_system import series_figure, style_figure
from physics_playground.visual.experience import PresentationLevel
from physics_playground.visual.tokens import LIGHT_THEME


def test_shared_chart_style_preserves_data_and_applies_visual_tokens():
    figure = series_figure(
        x=[0, 1, 2],
        series={"Measurement": [2, 3, 5]},
        x_label="Time (s)",
        y_label="Value (m)",
        title="Pilot chart",
    )
    axis = figure.axes[0]
    assert list(axis.lines[0].get_xdata()) == [0, 1, 2]
    assert list(axis.lines[0].get_ydata()) == [2, 3, 5]
    assert axis.get_facecolor()[:3] == tuple(
        int(LIGHT_THEME.surface[i : i + 2], 16) / 255 for i in (1, 3, 5)
    )
    style_figure(figure, PresentationLevel.DIAGRAM)
    assert axis.get_xlabel() == "Time (s)" and axis.get_ylabel() == "Value (m)"
    plt.close(figure)


def test_pilot_pages_retain_all_four_learning_modes():
    from physics_playground.subjects.light_and_electricity.thin_lenses import page as lens_page
    from physics_playground.subjects.mechanics.bumper_cars import page as bumper_page
    from physics_playground.subjects.mechanics.cannonball import page as cannon_page
    from physics_playground.subjects.mechanics.orbital_gravity import page as orbit_page
    from physics_playground.subjects.waves_and_oscillations.pendulum import page as pendulum_page

    sources = (cannon_page, pendulum_page, orbit_page, bumper_page, lens_page)
    for module in sources:
        source = open(module.__file__, encoding="utf-8").read()
        for mode in ("EXPLORE", "COMPARE", "ANALYZE", "MODEL"):
            assert mode in source
