import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import embed
from physics_playground.canvas.fluid_container import build_fluid_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import ui as mission_ui
from physics_playground.presentation.accessibility_ui import render_chart
from physics_playground.presentation.chart_system import series_figure
from physics_playground.presentation.learning_modes import (
    ChangedVariable,
    LearningMode,
    assumptions_panel,
    changed_variable_banner,
    mode_heading,
    mode_navigation,
)
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.state_keys import simulation_key
from physics_playground.units import EARTH_GRAVITY_M_S2, STANDARD_ATMOSPHERE_PA

from .missions import evaluate
from .physics import FluidPressureParameters, simulate

ID = "fluid_pressure"


def state_key(name: str) -> str:
    canonical = simulation_key(ID, name)
    if name in st.session_state and canonical not in st.session_state:
        st.session_state[canonical] = st.session_state.pop(name)
    return canonical


VERSION = "fluid-pressure-1.0"


def metrics(r):
    return {
        "depth_m": r.parameters.depth_m,
        "gauge_pressure_pa": r.gauge_pressure_pa,
        "absolute_pressure_pa": r.absolute_pressure_pa,
        "pressure_gradient_pa_m": r.pressure_increase_per_meter_pa,
    }


def record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id=ID,
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("pressure_quiz_guess")),
        result_summary=r.outcome,
        metrics=metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def diagram(r, seed):
    embed.show(
        build_fluid_document(
            kind="pressure",
            message=r.outcome,
            seed=seed,
            depth=r.parameters.depth_m,
            maximum_depth=r.parameters.maximum_depth_m,
            gauge_pressure=r.gauge_pressure_pa,
            absolute_pressure=r.absolute_pressure_pa,
            surface_pressure=r.parameters.surface_pressure_pa,
            fluid_density=r.parameters.fluid_density_kg_m3,
            pressure_samples=[
                {"depth": sample.depth_m, "gauge": sample.gauge_pressure_pa} for sample in r.samples
            ],
        ),
        height=570,
    )


def controls(prefix="pressure"):
    c = st.columns(3)
    density = c[0].slider(
        "Fluid density (kg/m³)", 100.0, 2000.0, 1000.0, 25.0, key=state_key(f"{prefix}_density")
    )
    maximum = c[1].slider(
        "Container depth (m)", 1.0, 50.0, 10.0, 1.0, key=state_key(f"{prefix}_max")
    )
    depth = c[2].slider(
        "Measurement depth (m)",
        0.0,
        float(maximum),
        min(5.0, float(maximum)),
        0.1,
        key=state_key(f"{prefix}_depth"),
    )
    gravity = st.slider(
        "Gravity (m/s²)", 1.0, 25.0, EARTH_GRAVITY_M_S2, 0.01, key=state_key(f"{prefix}_gravity")
    )
    surface = st.number_input(
        "Surface pressure (Pa)",
        min_value=0.0,
        max_value=200000.0,
        value=STANDARD_ATMOSPHERE_PA,
        step=100.0,
        key=state_key(f"{prefix}_surface"),
    )
    return FluidPressureParameters(density, depth, gravity, surface, maximum)


def explore():
    mode_heading(LearningMode.EXPLORE, "Measure pressure below the surface")
    r = simulate(controls())
    c = st.columns(3)
    c[0].metric("Gauge pressure", f"{r.gauge_pressure_pa / 1000:.2f} kPa")
    c[1].metric("Absolute pressure", f"{r.absolute_pressure_pa / 1000:.2f} kPa")
    c[2].metric("Increase per meter", f"{r.pressure_increase_per_meter_pa / 1000:.2f} kPa/m")
    st.caption("Text outcome: " + r.outcome)
    diagram(r, 20263201)
    obs = st.text_input("Optional notebook observation", key=state_key("pressure_obs"))
    if st.button("🌊 Measure pressure", type="primary", use_container_width=True):
        record(r, 20263201, obs, badges=mission_ui.process_run(ID, evaluate(r)))
        st.rerun()
    mission_ui.mission_checklist("Fluid Pressure")


def compare():
    mode_heading(LearningMode.COMPARE, "Shallow versus deep")
    a = simulate(FluidPressureParameters(depth_m=2))
    b = simulate(FluidPressureParameters(depth_m=8))
    changed_variable_banner(ChangedVariable("Depth", "2 m", "8 m"))
    c = st.columns(2)
    c[0].metric("2 m gauge", f"{a.gauge_pressure_pa / 1000:.1f} kPa")
    c[1].metric("8 m gauge", f"{b.gauge_pressure_pa / 1000:.1f} kPa")
    if st.button("▶ Run depth comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20263211), ("Run B", b, 20263212)):
            record(
                r,
                seed,
                "Pressure increases linearly with depth",
                label,
                mission_ui.process_run(ID, evaluate(r, True)),
            )
    diagram(b, 20263212)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Compare pressure throughout a column")
    r = simulate(controls("pressure_analysis"))
    figure = series_figure(
        x=[s.depth_m for s in r.samples],
        series={
            "Gauge pressure": [s.gauge_pressure_pa / 1000 for s in r.samples],
            "Absolute pressure": [s.absolute_pressure_pa / 1000 for s in r.samples],
        },
        x_label="Depth (m)",
        y_label="Pressure (kPa)",
        title="Hydrostatic pressure through the column",
    )
    render_chart(
        figure,
        "Both pressures increase linearly with depth; absolute pressure is gauge pressure shifted upward by surface pressure. Distinct line styles and markers identify the two series.",
    )
    plt.close(figure)


def model():
    mode_heading(LearningMode.MODEL, "Hydrostatic pressure")
    st.latex(r"P_{gauge}=\rho gh,\qquad P_{absolute}=P_{surface}+\rho gh")
    assumptions_panel(
        (
            ModelAssumption("static", "Fluid is at rest"),
            ModelAssumption("uniform", "Density and gravity are constant"),
        ),
        (
            "No compressibility or density stratification.",
            "No fluid acceleration or surface waves.",
            "Pressure depends on depth, not container shape.",
        ),
    )


def render():
    st.header("🌊 Fluid Pressure")
    revealed = mission_ui.prediction_quiz(
        key=state_key("pressure_quiz"),
        question="In a resting fluid, what happens to pressure as depth increases?",
        options=["It increases", "It decreases", "Container width decides"],
        correct_index=0,
        reveal_text="Each deeper layer supports more fluid above it, adding ρgh.",
        mission_id="pressure_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key=state_key("pressure_mode"))
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
