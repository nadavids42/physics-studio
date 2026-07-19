from __future__ import annotations

import streamlit as st

from physics_playground.canvas import embed
from physics_playground.canvas.gas_container import build_gas_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import ui as mission_ui
from physics_playground.presentation.learning_modes import (
    ChangedVariable,
    LearningMode,
    assumptions_panel,
    changed_variable_banner,
    mode_heading,
    mode_navigation,
    run_model_safely,
)
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.state_keys import simulation_key

from .charts import render_analysis_charts
from .missions import evaluate
from .physics import (
    GAS_LAWS_MODEL_VERSION,
    GasLawParameters,
    GasLawResult,
    GasLawScenario,
    celsius_to_kelvin,
    simulate,
)

ID = "gas_laws"
SEED = 20263301

ASSUMPTIONS = (
    ModelAssumption("ideal", "Particles have negligible volume and no intermolecular forces"),
    ModelAssumption("equilibrium", "Each state is uniform and equilibrated"),
)
LIMITATIONS = (
    "Real gases deviate at high pressure and low temperature.",
    "Processes jump between equilibrium states rather than model heat-transfer rates.",
    "No phase changes or chemical reactions.",
)


def state_key(name: str) -> str:
    canonical = simulation_key(ID, name)
    if name in st.session_state and canonical not in st.session_state:
        st.session_state[canonical] = st.session_state.pop(name)
    return canonical


def record(r, obs, label=None, badges=()):
    add_trial(
        simulation_id=ID,
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("gas_quiz_guess")),
        result_summary=r.outcome,
        metrics={
            "state_a_pressure_pa": r.state_a.pressure_pa,
            "state_a_volume_m3": r.state_a.volume_m3,
            "state_a_temperature_k": r.state_a.temperature_k,
            "state_b_pressure_pa": r.state_b.pressure_pa,
            "state_b_volume_m3": r.state_b.volume_m3,
            "state_b_temperature_k": r.state_b.temperature_k,
        },
        earned_badges=badges,
        random_seed=SEED,
        model_version=GAS_LAWS_MODEL_VERSION,
        learner_observation=obs,
        label=label,
    )


def diagram(result: GasLawResult, seed: int) -> None:
    embed.show(
        build_gas_document(
            pressure_a_kpa=result.state_a.pressure_pa / 1000,
            pressure_b_kpa=result.state_b.pressure_pa / 1000,
            volume_a_m3=result.state_a.volume_m3,
            volume_b_m3=result.state_b.volume_m3,
            temp_a_k=result.state_a.temperature_k,
            temp_b_k=result.state_b.temperature_k,
            particles=max(8, min(80, int(result.state_a.amount_mol * 20))),
            message=result.outcome,
            seed=seed,
            amount_mol=result.state_a.amount_mol,
        ),
        height=590,
    )


def controls(prefix: str = "gas") -> GasLawParameters:
    scenario = GasLawScenario(
        st.selectbox(
            "Gas-law scenario",
            [item.value for item in GasLawScenario],
            key=state_key(f"{prefix}_scenario"),
        )
    )
    columns = st.columns(4)
    amount = columns[0].slider("Amount (mol)", 0.1, 5.0, 1.0, 0.1, key=state_key(f"{prefix}_n"))
    pressure_kpa = columns[1].slider(
        "Constant pressure (kPa)",
        20.0,
        500.0,
        101.325,
        0.5,
        key=state_key(f"{prefix}_p"),
        disabled=scenario is not GasLawScenario.CHARLES,
    )
    volume_l = columns[2].slider(
        "Initial/constant volume (L)",
        1.0,
        100.0,
        24.0,
        1.0,
        key=state_key(f"{prefix}_v"),
    )
    temperature_c = columns[3].slider(
        "Initial temperature (°C)",
        -250.0,
        500.0,
        20.0,
        1.0,
        key=state_key(f"{prefix}_t"),
    )
    target_volume_l = st.slider(
        "Target volume for Boyle's law (L)",
        1.0,
        100.0,
        12.0,
        1.0,
        key=state_key(f"{prefix}_target_v"),
        disabled=scenario is not GasLawScenario.BOYLE,
    )
    target_temperature_c = st.slider(
        "Target temperature (°C)",
        -250.0,
        500.0,
        100.0,
        1.0,
        key=state_key(f"{prefix}_target_t"),
        disabled=scenario not in (GasLawScenario.CHARLES, GasLawScenario.GAY_LUSSAC),
    )
    st.caption(
        f"Converted absolute temperatures: {celsius_to_kelvin(temperature_c):.2f} K → "
        f"{celsius_to_kelvin(target_temperature_c):.2f} K. Physics calculations use Pa, "
        "m³, K, and mol."
    )
    return GasLawParameters(
        scenario,
        amount,
        pressure_kpa * 1000,
        volume_l / 1000,
        celsius_to_kelvin(temperature_c),
        target_volume_l / 1000,
        celsius_to_kelvin(target_temperature_c),
    )


def state_table(result: GasLawResult) -> None:
    st.markdown(
        "| State | Pressure | Volume | Temperature | Amount |\n|---|---:|---:|---:|---:|\n"
        f"| A | {result.state_a.pressure_pa / 1000:.2f} kPa | "
        f"{result.state_a.volume_m3 * 1000:.2f} L | {result.state_a.temperature_k:.2f} K | "
        f"{result.state_a.amount_mol:.2f} mol |\n"
        f"| B | {result.state_b.pressure_pa / 1000:.2f} kPa | "
        f"{result.state_b.volume_m3 * 1000:.2f} L | {result.state_b.temperature_k:.2f} K | "
        f"{result.state_b.amount_mol:.2f} mol |"
    )


def invariant_metric(result: GasLawResult) -> None:
    difference = result.invariant_b - result.invariant_a
    st.metric(result.invariant_name + " difference", f"{difference:.3g}")


def explore() -> None:
    mode_heading(LearningMode.EXPLORE, "Constrain a gas process")
    parameters = controls()
    result = run_model_safely(lambda: simulate(parameters))
    if result is None:
        return
    state_table(result)
    invariant_metric(result)
    st.caption("Text outcome: " + result.outcome)
    diagram(result, SEED)
    observation = st.text_input("Optional notebook observation", key=state_key("gas_obs"))
    if st.button("🎈 Run gas experiment", type="primary", use_container_width=True):
        committed = run_model_safely(lambda: simulate(parameters))
        if committed is not None:
            badges = mission_ui.process_run(ID, evaluate(committed))
            record(
                committed,
                observation,
                badges=badges,
            )
            st.rerun()
    mission_ui.mission_checklist("Gas Laws")


def compare() -> None:
    mode_heading(LearningMode.COMPARE, "Compression versus heating")
    run_a = run_model_safely(
        lambda: simulate(GasLawParameters(GasLawScenario.BOYLE, target_volume_m3=0.012))
    )
    run_b = run_model_safely(
        lambda: simulate(GasLawParameters(GasLawScenario.GAY_LUSSAC, target_temperature_k=373.15))
    )
    if run_a is None or run_b is None:
        return
    changed_variable_banner(
        ChangedVariable("Process", "Isothermal compression", "Isochoric heating")
    )
    columns = st.columns(2)
    columns[0].metric("Compressed pressure", f"{run_a.state_b.pressure_pa / 1000:.1f} kPa")
    columns[1].metric("Heated pressure", f"{run_b.state_b.pressure_pa / 1000:.1f} kPa")
    if st.button("▶ Run process comparison", use_container_width=True):
        for label, result in (("Run A", run_a), ("Run B", run_b)):
            badges = mission_ui.process_run(ID, evaluate(result, True))
            record(
                result,
                "Different constraints produce different state paths",
                label,
                badges,
            )
    diagram(run_b, 20263312)


def analyze() -> None:
    mode_heading(LearningMode.ANALYZE, "P–V, V–T, and P–T relationships")
    amount = st.slider("Analysis amount (mol)", 0.1, 5.0, 1.0, 0.1)
    temperature = celsius_to_kelvin(st.slider("P–V temperature (°C)", -200.0, 400.0, 20.0, 1.0))
    pressure = st.slider("V–T pressure (kPa)", 20.0, 500.0, 101.325, 0.5) * 1000
    volume = st.slider("P–T volume (L)", 1.0, 100.0, 24.0, 1.0) / 1000
    render_analysis_charts(
        amount_mol=amount,
        temperature_k=temperature,
        pressure_pa=pressure,
        volume_m3=volume,
    )


def model() -> None:
    mode_heading(LearningMode.MODEL, "One equation, three constrained laws")
    st.latex(r"PV=nRT")
    st.latex(
        r"\text{Boyle: }PV=\text{constant}\quad \text{Charles: }V/T=\text{constant}\quad "
        r"\text{Gay-Lussac: }P/T=\text{constant}"
    )
    st.markdown(
        "Temperature ratios must use kelvin, never Celsius. The interface converts liters→m³, "
        "kPa→Pa, and °C→K before calculation."
    )
    assumptions_panel(ASSUMPTIONS, LIMITATIONS)


def render() -> None:
    st.header("🎈 Gas Laws")
    revealed = mission_ui.prediction_quiz(
        key=state_key("gas_quiz"),
        question=(
            "At constant temperature, what happens to ideal-gas pressure when volume is cut in half?"
        ),
        options=["It doubles", "It halves", "It stays fixed"],
        correct_index=0,
        reveal_text="Boyle's law keeps PV constant, so halving V doubles P.",
        mission_id="gas_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key=state_key("gas_mode"))
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
