"""Static analytical charts for typed projectile results."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from physics_playground.contracts import PlotData


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
