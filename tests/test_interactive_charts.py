import pytest

from physics_playground.models.charts import (
    ChartAxis,
    ChartLineStyle,
    ChartMarker,
    InteractiveChart,
    InteractiveSeries,
)
from physics_playground.presentation.interactive_charts import (
    build_chart_document,
    interactive_chart_cache_info,
)
from physics_playground.subjects.mechanics.cannonball.charts import (
    range_by_angle_chart,
    trajectory_comparison_chart,
)
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    simulate_no_drag,
)


def sample_chart() -> InteractiveChart:
    return InteractiveChart(
        "sample",
        "Position comparison",
        "Two distinct runs shown with exact values.",
        ChartAxis("Time", "s"),
        ChartAxis("Position", "m"),
        (
            InteractiveSeries(
                "a",
                "Run A",
                (0.0, 1.0),
                (0.0, 2.0),
                "graph_1",
                ChartLineStyle.SOLID,
                ChartMarker.CIRCLE,
            ),
            InteractiveSeries(
                "b",
                "Run B",
                (0.0, 1.0),
                (0.0, 1.0),
                "graph_2",
                ChartLineStyle.DASHED,
                ChartMarker.SQUARE,
            ),
        ),
        zoom=True,
    )


def test_chart_contract_preserves_units_and_color_independent_encoding():
    payload = sample_chart().to_dict()
    assert payload["x_axis"]["display_label"] == "Time (s)"
    assert payload["y_axis"]["display_label"] == "Position (m)"
    assert payload["series"][0]["line_style"] == "solid"
    assert payload["series"][1]["line_style"] == "dashed"
    assert payload["series"][0]["marker"] != payload["series"][1]["marker"]


def test_chart_contract_rejects_mismatched_or_nonfinite_coordinates():
    with pytest.raises(ValueError, match="equal nonempty"):
        InteractiveSeries("bad", "Bad", (1.0,), (), "graph_1").validate()
    with pytest.raises(ValueError, match="finite"):
        InteractiveSeries("bad", "Bad", (1.0,), (float("nan"),), "graph_1").validate()


def test_chart_document_has_svg_description_table_and_interaction_contract():
    document = build_chart_document(sample_chart())
    assert 'role="img"' in document
    assert "Two distinct runs shown with exact values." in document
    assert "Data table" in document and 'tabindex="0"' in document
    assert '"linked_highlight":true' in document
    assert '"zoom":true' in document


def test_chart_document_cache_is_parameter_sensitive_and_bounded():
    first = sample_chart()
    build_chart_document(first)
    before = interactive_chart_cache_info()
    assert build_chart_document(first) == build_chart_document(first)
    after = interactive_chart_cache_info()
    assert after.hits > before.hits and after.maxsize == 128
    changed = InteractiveChart(
        first.id,
        first.title,
        first.description,
        first.x_axis,
        first.y_axis,
        (InteractiveSeries("a", "Run A", (0.0, 1.0), (0.0, 3.0)),),
    )
    assert build_chart_document(changed) != build_chart_document(first)


def test_cannonball_compare_and_analyze_adapters_preserve_physics_samples():
    first = simulate_no_drag(ProjectileParameters(25, 30))
    second = simulate_no_drag(ProjectileParameters(25, 60))
    comparison = trajectory_comparison_chart(first, second, ("30 degrees", "60 degrees"))
    assert comparison.series[0].x == first.animation.tracks[0].x
    assert comparison.series[1].y == second.animation.tracks[0].y
    assert "Trajectory comparison" in build_chart_document(comparison)
    scan = range_by_angle_chart(25, 9.81)
    assert scan.x_axis.unit == "degrees" and scan.y_axis.unit == "m"
    assert scan.zoom and scan.table and scan.hover
