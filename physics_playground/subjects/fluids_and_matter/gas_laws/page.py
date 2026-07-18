import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import legacy
from physics_playground.canvas.gas_container import build_gas_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.accessibility import render_chart
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

from .missions import evaluate
from .physics import (
    GAS_CONSTANT_J_MOL_K,
    GasLawParameters,
    GasLawScenario,
    celsius_to_kelvin,
    simulate,
)

ID = "gas_laws"
VERSION = "gas-laws-1.0"


def metrics(r):
    return {
        "state_a_pressure_pa": r.state_a.pressure_pa,
        "state_a_volume_m3": r.state_a.volume_m3,
        "state_a_temperature_k": r.state_a.temperature_k,
        "state_b_pressure_pa": r.state_b.pressure_pa,
        "state_b_volume_m3": r.state_b.volume_m3,
        "state_b_temperature_k": r.state_b.temperature_k,
        "invariant_difference": r.invariant_b - r.invariant_a,
    }


def record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id=ID,
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get("gas_quiz_guess"),
        result_summary=r.outcome,
        metrics=metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def diagram(r, seed):
    legacy.show(
        build_gas_document(
            pressure_a_kpa=r.state_a.pressure_pa / 1000,
            pressure_b_kpa=r.state_b.pressure_pa / 1000,
            volume_a_m3=r.state_a.volume_m3,
            volume_b_m3=r.state_b.volume_m3,
            temp_a_k=r.state_a.temperature_k,
            temp_b_k=r.state_b.temperature_k,
            particles=max(8, min(80, int(r.state_a.amount_mol * 20))),
            message=r.outcome,
            seed=seed,
            amount_mol=r.state_a.amount_mol,
        ),
        height=590,
    )


def controls(prefix="gas"):
    scenario = GasLawScenario(
        st.selectbox(
            "Gas-law scenario", [x.value for x in GasLawScenario], key=f"{prefix}_scenario"
        )
    )
    c = st.columns(4)
    n = c[0].slider("Amount (mol)", 0.1, 5.0, 1.0, 0.1, key=f"{prefix}_n")
    pressure_kpa = c[1].slider(
        "Constant pressure (kPa)",
        20.0,
        500.0,
        101.325,
        0.5,
        key=f"{prefix}_p",
        disabled=scenario not in (GasLawScenario.CHARLES,),
    )
    volume_l = c[2].slider("Initial/constant volume (L)", 1.0, 100.0, 24.0, 1.0, key=f"{prefix}_v")
    temp_c = c[3].slider("Initial temperature (°C)", -250.0, 500.0, 20.0, 1.0, key=f"{prefix}_t")
    target_volume_l = st.slider(
        "Target volume for Boyle's law (L)",
        1.0,
        100.0,
        12.0,
        1.0,
        key=f"{prefix}_target_v",
        disabled=scenario is not GasLawScenario.BOYLE,
    )
    target_temp_c = st.slider(
        "Target temperature (°C)",
        -250.0,
        500.0,
        100.0,
        1.0,
        key=f"{prefix}_target_t",
        disabled=scenario not in (GasLawScenario.CHARLES, GasLawScenario.GAY_LUSSAC),
    )
    st.caption(
        f"Converted absolute temperatures: {celsius_to_kelvin(temp_c):.2f} K → {celsius_to_kelvin(target_temp_c):.2f} K. Physics calculations use Pa, m³, K, and mol."
    )
    return GasLawParameters(
        scenario,
        n,
        pressure_kpa * 1000,
        volume_l / 1000,
        celsius_to_kelvin(temp_c),
        target_volume_l / 1000,
        celsius_to_kelvin(target_temp_c),
    )


def state_table(r):
    st.markdown(
        "| State | Pressure | Volume | Temperature | Amount |\n|---|---:|---:|---:|---:|\n"
        + f"| A | {r.state_a.pressure_pa / 1000:.2f} kPa | {r.state_a.volume_m3 * 1000:.2f} L | {r.state_a.temperature_k:.2f} K | {r.state_a.amount_mol:.2f} mol |\n"
        + f"| B | {r.state_b.pressure_pa / 1000:.2f} kPa | {r.state_b.volume_m3 * 1000:.2f} L | {r.state_b.temperature_k:.2f} K | {r.state_b.amount_mol:.2f} mol |"
    )


def explore():
    mode_heading(LearningMode.EXPLORE, "Constrain a gas process")
    r = simulate(controls())
    state_table(r)
    st.metric(r.invariant_name + " difference", f"{r.invariant_b - r.invariant_a:.3g}")
    st.caption("Text outcome: " + r.outcome)
    diagram(r, 20263301)
    obs = st.text_input("Optional notebook observation", key="gas_obs")
    if st.button("🎈 Run gas experiment", type="primary", use_container_width=True):
        record(r, 20263301, obs, badges=kidtools.process_run(ID, evaluate(r)))
        st.rerun()
    kidtools.mission_checklist("Gas Laws")


def compare():
    mode_heading(LearningMode.COMPARE, "Compression versus heating")
    a = simulate(GasLawParameters(GasLawScenario.BOYLE, target_volume_m3=0.012))
    b = simulate(GasLawParameters(GasLawScenario.GAY_LUSSAC, target_temperature_k=373.15))
    changed_variable_banner(
        ChangedVariable("Process", "Isothermal compression", "Isochoric heating")
    )
    c = st.columns(2)
    c[0].metric("Compressed pressure", f"{a.state_b.pressure_pa / 1000:.1f} kPa")
    c[1].metric("Heated pressure", f"{b.state_b.pressure_pa / 1000:.1f} kPa")
    if st.button("▶ Run process comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20263311), ("Run B", b, 20263312)):
            record(
                r,
                seed,
                "Different constraints produce different state paths",
                label,
                kidtools.process_run(ID, evaluate(r, True)),
            )
    diagram(b, 20263312)


def analyze():
    mode_heading(LearningMode.ANALYZE, "P–V, V–T, and P–T relationships")
    n = st.slider("Analysis amount (mol)", 0.1, 5.0, 1.0, 0.1)
    temperature = celsius_to_kelvin(st.slider("P–V temperature (°C)", -200.0, 400.0, 20.0, 1.0))
    pressure = st.slider("V–T pressure (kPa)", 20.0, 500.0, 101.325, 0.5) * 1000
    volume = st.slider("P–T volume (L)", 1.0, 100.0, 24.0, 1.0) / 1000
    volumes = [x / 1000 for x in range(2, 101, 2)]
    pv = series_figure(
        x=[v * 1000 for v in volumes],
        series={"Pressure": [n * GAS_CONSTANT_J_MOL_K * temperature / v / 1000 for v in volumes]},
        x_label="Volume (L)",
        y_label="Pressure (kPa)",
        title="Boyle relationship at constant temperature",
    )
    render_chart(
        pv,
        "At constant temperature and amount, pressure decreases hyperbolically as volume increases.",
    )
    plt.close(pv)
    temperatures = list(range(50, 751, 10))
    vt = series_figure(
        x=temperatures,
        series={"Volume": [n * GAS_CONSTANT_J_MOL_K * t / pressure * 1000 for t in temperatures]},
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
        series={"Pressure": [n * GAS_CONSTANT_J_MOL_K * t / volume / 1000 for t in temperatures]},
        x_label="Temperature (K)",
        y_label="Pressure (kPa)",
        title="Gay-Lussac relationship at constant volume",
    )
    render_chart(
        pt, "At constant volume and amount, pressure increases linearly with absolute temperature."
    )
    plt.close(pt)


def model():
    mode_heading(LearningMode.MODEL, "One equation, three constrained laws")
    st.latex(r"PV=nRT")
    st.latex(
        r"\text{Boyle: }PV=\text{constant}\quad \text{Charles: }V/T=\text{constant}\quad \text{Gay-Lussac: }P/T=\text{constant}"
    )
    st.markdown(
        "Temperature ratios must use kelvin, never Celsius. The interface converts liters→m³, kPa→Pa, and °C→K before calculation."
    )
    assumptions_panel(
        (
            ModelAssumption(
                "ideal", "Particles have negligible volume and no intermolecular forces"
            ),
            ModelAssumption("equilibrium", "Each state is uniform and equilibrated"),
        ),
        (
            "Real gases deviate at high pressure and low temperature.",
            "Processes jump between equilibrium states rather than model heat-transfer rates.",
            "No phase changes or chemical reactions.",
        ),
    )


def render():
    st.header("🎈 Gas Laws")
    revealed = kidtools.prediction_quiz(
        key="gas_quiz",
        question="At constant temperature, what happens to ideal-gas pressure when volume is cut in half?",
        options=["It doubles", "It halves", "It stays fixed"],
        correct_index=0,
        reveal_text="Boyle's law keeps PV constant, so halving V doubles P.",
        mission_id="gas_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key="gas_mode")
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
