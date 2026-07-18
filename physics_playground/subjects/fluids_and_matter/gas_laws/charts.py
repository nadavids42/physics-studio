"""Gas-law-specific analytical chart composition."""

from __future__ import annotations

import matplotlib.pyplot as plt

from physics_playground.presentation.accessibility_ui import render_chart
from physics_playground.presentation.chart_system import series_figure

from .physics import GAS_CONSTANT_J_MOL_K


def render_analysis_charts(
    *, amount_mol: float, temperature_k: float, pressure_pa: float, volume_m3: float
) -> None:
    volumes = [value / 1000 for value in range(2, 101, 2)]
    pv = series_figure(
        x=[value * 1000 for value in volumes],
        series={
            "Pressure": [
                amount_mol * GAS_CONSTANT_J_MOL_K * temperature_k / value / 1000
                for value in volumes
            ]
        },
        x_label="Volume (L)",
        y_label="Pressure (kPa)",
        title="Boyle relationship at constant temperature",
    )
    render_chart(
        pv,
        "At constant temperature and amount, pressure decreases hyperbolically as volume increases.",
    )
    plt.close(pv)

    temperatures = [float(value) for value in range(50, 751, 10)]
    vt = series_figure(
        x=temperatures,
        series={
            "Volume": [
                amount_mol * GAS_CONSTANT_J_MOL_K * value / pressure_pa * 1000
                for value in temperatures
            ]
        },
        x_label="Temperature (K)",
        y_label="Volume (L)",
        title="Charles relationship at constant pressure",
    )
    render_chart(
        vt, "At constant pressure and amount, volume increases linearly with absolute temperature."
    )
    plt.close(vt)

    pt = series_figure(
        x=temperatures,
        series={
            "Pressure": [
                amount_mol * GAS_CONSTANT_J_MOL_K * value / volume_m3 / 1000
                for value in temperatures
            ]
        },
        x_label="Temperature (K)",
        y_label="Pressure (kPa)",
        title="Gay-Lussac relationship at constant volume",
    )
    render_chart(
        pt, "At constant volume and amount, pressure increases linearly with absolute temperature."
    )
    plt.close(pt)
