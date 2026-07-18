"""Static analytical charts for typed pendulum results."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from physics_playground.subjects.waves_and_oscillations.pendulum.physics import (
    approximation_error_curve,
)


def plot_figure(plot, overlays=()) -> Figure:
    fig, ax = plt.subplots()
    for item in (plot, *overlays):
        for s in item.series:
            ax.plot(s.x, s.y, label=s.label)
    ax.set_xlabel(plot.x_label)
    ax.set_ylabel(plot.y_label)
    ax.set_title(plot.title)
    ax.grid(True)
    if overlays:
        ax.legend()
    return fig


def error_figure(length, gravity) -> Figure:
    a, e = approximation_error_curve(length, gravity)
    fig, ax = plt.subplots()
    ax.plot(a, e)
    ax.set_xlabel("Release angle (degrees)")
    ax.set_ylabel("Period error (%)")
    ax.set_title("Small-angle approximation error")
    ax.grid(True)
    return fig
