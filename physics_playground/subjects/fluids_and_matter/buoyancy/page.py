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

from .missions import evaluate
from .physics import BuoyancyInputMode, BuoyancyParameters, simulate

ID = "buoyancy"


def state_key(name: str) -> str:
    canonical = simulation_key(ID, name)
    if name in st.session_state and canonical not in st.session_state:
        st.session_state[canonical] = st.session_state.pop(name)
    return canonical


VERSION = "buoyancy-1.0"


def metrics(r):
    return {
        "object_density_kg_m3": r.effective_density_kg_m3,
        "object_mass_kg": r.effective_mass_kg,
        "submerged_fraction": r.submerged_fraction,
        "buoyant_force_n": r.buoyant_force_n,
        "apparent_weight_n": r.apparent_weight_n,
        "net_vertical_force_n": r.net_vertical_force_n,
    }


def record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id=ID,
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("buoy_quiz_guess")),
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
            kind="buoyancy",
            message=r.outcome,
            seed=seed,
            submerged_fraction=r.submerged_fraction,
            state=r.state.value,
            object_density=r.effective_density_kg_m3,
            fluid_density=r.parameters.fluid_density_kg_m3,
            displaced_volume=r.displaced_volume_m3,
            weight=r.weight_n,
            buoyant_force=r.buoyant_force_n,
        ),
        height=570,
    )


def controls(prefix="buoy"):
    mode = BuoyancyInputMode(
        st.radio(
            "Define object using",
            [x.value for x in BuoyancyInputMode],
            horizontal=True,
            key=state_key(f"{prefix}_input_basis"),
        )
    )
    c = st.columns(3)
    density = c[0].slider(
        "Object density (kg/m³)",
        50.0,
        5000.0,
        600.0,
        25.0,
        key=state_key(f"{prefix}_density"),
        disabled=mode is BuoyancyInputMode.MASS,
    )
    mass = c[1].slider(
        "Object mass (kg)",
        0.1,
        100.0,
        6.0,
        0.1,
        key=state_key(f"{prefix}_mass"),
        disabled=mode is BuoyancyInputMode.DENSITY,
    )
    volume = c[2].slider(
        "Object volume (m³)", 0.001, 0.1, 0.01, 0.001, key=state_key(f"{prefix}_volume")
    )
    fluid = st.slider(
        "Fluid density (kg/m³)", 100.0, 2000.0, 1000.0, 25.0, key=state_key(f"{prefix}_fluid")
    )
    return BuoyancyParameters(mode, density, mass, volume, fluid)


def explore():
    mode_heading(LearningMode.EXPLORE, "Float, sink, or hover")
    r = simulate(controls())
    c = st.columns(3)
    c[0].metric("State", r.state.value)
    c[1].metric("Submerged", f"{r.submerged_fraction:.1%}")
    c[2].metric("Apparent weight", f"{r.apparent_weight_n:.2f} N")
    st.caption("Text outcome: " + r.outcome)
    diagram(r, 20263101)
    obs = st.text_input("Optional notebook observation", key=state_key("buoy_obs"))
    if st.button("🛟 Test buoyancy", type="primary", use_container_width=True):
        record(r, 20263101, obs, badges=mission_ui.process_run(ID, evaluate(r)))
        st.rerun()
    mission_ui.mission_checklist("Buoyancy")


def compare():
    mode_heading(LearningMode.COMPARE, "Water versus denser fluid")
    a = simulate(BuoyancyParameters(fluid_density_kg_m3=1000))
    b = simulate(BuoyancyParameters(fluid_density_kg_m3=1400))
    changed_variable_banner(ChangedVariable("Fluid density", "1000 kg/m³", "1400 kg/m³"))
    c = st.columns(2)
    c[0].metric("Water submerged", f"{a.submerged_fraction:.1%}")
    c[1].metric("Dense fluid submerged", f"{b.submerged_fraction:.1%}")
    if st.button("▶ Run fluid comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20263111), ("Run B", b, 20263112)):
            record(
                r,
                seed,
                "Denser fluid needs less displaced volume",
                label,
                mission_ui.process_run(ID, evaluate(r, True)),
            )
    diagram(b, 20263112)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Density ratio and submerged fraction")
    fluid = st.slider("Analysis fluid density (kg/m³)", 200.0, 2000.0, 1000.0, 25.0)
    densities = list(range(100, 2501, 50))
    results = [
        simulate(BuoyancyParameters(object_density_kg_m3=d, fluid_density_kg_m3=fluid))
        for d in densities
    ]
    fraction_figure = series_figure(
        x=densities,
        series={"Submerged fraction": [r.submerged_fraction for r in results]},
        x_label="Object density (kg/m³)",
        y_label="Submerged fraction",
        title="Submerged fraction versus density",
    )
    render_chart(
        fraction_figure,
        "Floating objects submerge in direct proportion to density ratio until they become fully submerged.",
    )
    plt.close(fraction_figure)
    weight_figure = series_figure(
        x=densities,
        series={"Apparent weight": [r.apparent_weight_n for r in results]},
        x_label="Object density (kg/m³)",
        y_label="Apparent weight (N)",
        title="Apparent weight versus density",
    )
    render_chart(
        weight_figure,
        "Objects denser than the fluid sink and retain positive apparent weight; floating objects have zero apparent weight in this static model.",
    )
    plt.close(weight_figure)


def model():
    mode_heading(LearningMode.MODEL, "Archimedes' principle")
    st.latex(r"F_B=\rho_fV_{displaced}g,\qquad W=mg")
    st.latex(r"\text{floating: }\frac{V_{sub}}{V}=\frac{\rho_o}{\rho_f}")
    assumptions_panel(
        (
            ModelAssumption("uniform", "Object and fluid densities are uniform"),
            ModelAssumption("static", "Final static equilibrium or fully submerged state"),
        ),
        (
            "No surface tension or fluid motion.",
            "The container is large enough to ignore boundaries.",
            "Sinking dynamics and drag are not simulated.",
        ),
    )


def render():
    st.header("🛟 Buoyancy")
    revealed = mission_ui.prediction_quiz(
        key=state_key("buoy_quiz"),
        question="An object is less dense than its fluid. What happens after it settles?",
        options=["It floats partly submerged", "It sinks", "It must hover fully submerged"],
        correct_index=0,
        reveal_text="It displaces enough fluid for buoyant force to balance its weight.",
        mission_id="buoy_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key=state_key("buoy_mode"))
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
