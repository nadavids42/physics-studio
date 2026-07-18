"""Analytical chart construction for Bumper Cars."""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from physics_playground.contracts import PlotData
from physics_playground.models.collision import CollisionParameters


def position_figure(plot: PlotData, collision_time_s: float | None) -> Figure:
    fig, ax = plt.subplots()
    for series in plot.series:
        ax.plot(series.x, series.y, label=series.label, color=series.color)
    if collision_time_s is not None:
        ax.axvline(collision_time_s, linestyle="--", linewidth=1, color="gray", label="Impact")
    ax.set_xlabel(plot.x_label)
    ax.set_ylabel(plot.y_label)
    ax.set_title(plot.title)
    ax.legend()
    ax.grid(True)
    return fig


def energy_retention_figure(parameters: CollisionParameters) -> Figure:
    from physics_playground.models.collision import collision_energy_scan

    restitutions, retained = collision_energy_scan(
        parameters.mass_a_kg,
        parameters.mass_b_kg,
        parameters.velocity_a_m_s,
        parameters.velocity_b_m_s,
    )
    fig, ax = plt.subplots()
    ax.plot(restitutions, retained)
    ax.set_xlabel("Restitution coefficient e")
    ax.set_ylabel("Fraction of kinetic energy retained")
    ax.set_title("Only e = 1 keeps all kinetic energy")
    ax.grid(True)
    return fig
