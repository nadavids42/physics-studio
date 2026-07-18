"""Static analytical charts for typed projectile results."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from physics_playground.contracts import PlotData
from physics_playground.models.charts import (
    ChartAxis,
    ChartLineStyle,
    ChartMarker,
    InteractiveChart,
    InteractiveSeries,
)
from physics_playground.performance import timed
from physics_playground.subjects.mechanics.cannonball.physics import ProjectileResult


def trajectory_comparison_chart(
    first: ProjectileResult, second: ProjectileResult, labels: tuple[str, str]
) -> InteractiveChart:
    if first.animation is None or second.animation is None:
        raise ValueError("Trajectory comparison requires animation coordinates.")
    tracks = (first.animation.tracks[0], second.animation.tracks[0])
    return InteractiveChart(
        "cannonball-trajectory-comparison",
        "Trajectory comparison",
        "Two projectile paths. Hover or focus the table to identify each run and compare height at horizontal position.",
        ChartAxis("Horizontal position", "m"),
        ChartAxis("Height", "m"),
        (
            InteractiveSeries(
                "run-a",
                labels[0],
                tracks[0].x,
                tracks[0].y or (),
                "graph_1",
                ChartLineStyle.SOLID,
                ChartMarker.CIRCLE,
            ),
            InteractiveSeries(
                "run-b",
                labels[1],
                tracks[1].x,
                tracks[1].y or (),
                "graph_2",
                ChartLineStyle.DASHED,
                ChartMarker.SQUARE,
            ),
        ),
        zoom=True,
    )


def range_by_angle_chart(speed_m_s: float, gravity_m_s2: float) -> InteractiveChart:
    from physics_playground.subjects.mechanics.cannonball.physics import projectile_range_scan

    angles, ranges = projectile_range_scan(speed_m_s, gravity_m_s2)
    return InteractiveChart(
        "cannonball-range-by-angle",
        "Range versus launch angle",
        "Ideal level-ground range rises toward 45 degrees and falls symmetrically. Hover for exact values or zoom around the maximum.",
        ChartAxis("Launch angle", "degrees"),
        ChartAxis("Range", "m"),
        (
            InteractiveSeries(
                "ideal-range",
                "Ideal range",
                tuple(float(value) for value in angles),
                ranges,
                "graph_1",
                ChartLineStyle.SOLID,
                ChartMarker.TRIANGLE,
            ),
        ),
        zoom=True,
    )


def plot_figure(plot: PlotData, overlays: tuple[PlotData, ...] = ()) -> Figure:
    fig, ax = plt.subplots()
    for item in (plot, *overlays):
        for series in item.series:
            ax.plot(series.x, series.y, label=series.label)
    ax.set_xlabel(plot.x_label)
    ax.set_ylabel(plot.y_label)
    ax.set_title(plot.title)
    ax.grid(True)
    if overlays or len(plot.series) > 1:
        ax.legend()
    return fig


@timed("chart.cannonball.range_by_angle")
def range_by_angle_figure(speed_m_s: float, gravity_m_s2: float) -> Figure:
    from physics_playground.subjects.mechanics.cannonball.physics import projectile_range_scan

    angles, ranges = projectile_range_scan(speed_m_s, gravity_m_s2)
    fig, ax = plt.subplots()
    ax.plot(list(angles), ranges)
    ax.axvline(45, color="crimson", linestyle="--")
    ax.set_xlabel("Launch angle (degrees)")
    ax.set_ylabel("Range (m)")
    ax.set_title("Maximum no-drag range occurs near 45°")
    ax.grid(True)
    return fig
