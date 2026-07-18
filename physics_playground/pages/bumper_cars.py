"""Four-mode Streamlit learning experience for Bumper Cars."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import legacy as canvas_kit
from physics_playground.canvas.bumper_cars import (
    PLAYER_HEIGHT,
    build_bumper_canvas,
    build_bumper_comparison_canvas,
)
from physics_playground.missions import legacy as kidtools
from physics_playground.missions.bumper_cars import evaluate_bumper_missions
from physics_playground.models.collision import (
    CollisionParameters,
    CollisionResult,
)
from physics_playground.presentation.accessibility import render_chart
from physics_playground.presentation.bumper_cars import energy_retention_figure, position_figure
from physics_playground.presentation.bumper_learning import comparison_measurements
from physics_playground.presentation.learning_modes import (
    ChangedVariable,
    LearningMode,
    assumptions_panel,
    changed_variable_banner,
    comparison_metrics,
    mode_heading,
    mode_navigation,
)
from physics_playground.presentation.notebook_ui import REUSE_REQUEST_KEY, add_trial, get_notebook
from physics_playground.simulation_cache import cached_collision as simulate_collision
from physics_playground.validation import PhysicsValidationError

LAUNCH_NONCE_KEY = "bumper_launch_nonce"
LAUNCHED_PARAMETERS_KEY = "bumper_launched_parameters"
COMPARE_NONCE_KEY = "bumper_compare_nonce"
COMPARE_SIGNATURE_KEY = "bumper_compare_signature"
BUMPER_MODEL_VERSION = "collision-1.0"


def _initialize_state() -> None:
    st.session_state.setdefault(LAUNCH_NONCE_KEY, 0)
    st.session_state.setdefault(LAUNCHED_PARAMETERS_KEY, None)
    st.session_state.setdefault(COMPARE_NONCE_KEY, 0)
    st.session_state.setdefault(COMPARE_SIGNATURE_KEY, None)


def _award_launched_missions(result: CollisionResult) -> tuple[str, ...]:
    return kidtools.process_run("bumper_cars", evaluate_bumper_missions(result))


def _outcome_message(result: CollisionResult) -> str:
    if not result.collided:
        return "No crash this time—the cars never catch each other."
    after = result.velocities_after
    if result.parameters.restitution == 0:
        return f"🧲 CLANG! They stuck together and rolled off at {after.car_a_m_s:.1f} m/s."
    return f"💥 BONK! Car A: {after.car_a_m_s:.1f} m/s, Car B: {after.car_b_m_s:.1f} m/s."


def _notebook_metrics(result: CollisionResult) -> dict[str, float]:
    return {
        "velocity_a_after_m_s": result.velocities_after.car_a_m_s,
        "velocity_b_after_m_s": result.velocities_after.car_b_m_s,
        "momentum_before_kg_m_s": result.diagnostics.momentum_before_kg_m_s,
        "momentum_after_kg_m_s": result.diagnostics.momentum_after_kg_m_s,
        "kinetic_energy_before_j": result.diagnostics.kinetic_energy_before_j,
        "kinetic_energy_after_j": result.diagnostics.kinetic_energy_after_j,
        "energy_lost_j": result.diagnostics.energy_lost_j,
        "center_of_mass_velocity_m_s": result.diagnostics.center_of_mass_velocity_m_s,
        "collision_time_s": result.collision_time_s or 0.0,
    }


def _record_trial(
    result: CollisionResult,
    *,
    seed: int,
    observation: str | None,
    label: str | None = None,
    badges: tuple[str, ...] = (),
) -> None:
    add_trial(
        simulation_id="bumper_cars",
        parameters=result.parameters.to_dict(),
        prediction=st.session_state.get("collision_quiz_guess"),
        result_summary=_outcome_message(result),
        metrics=_notebook_metrics(result),
        earned_badges=badges,
        random_seed=seed,
        model_version=BUMPER_MODEL_VERSION,
        learner_observation=observation,
        label=label,
    )


def _apply_reuse_request() -> None:
    request = st.session_state.get(REUSE_REQUEST_KEY)
    if not request or request.get("simulation_id") != "bumper_cars":
        return
    parameters = request["parameters"]
    st.session_state["explore_mass_a"] = min(5.0, max(0.5, float(parameters["mass_a_kg"])))
    st.session_state["explore_mass_b"] = min(5.0, max(0.5, float(parameters["mass_b_kg"])))
    st.session_state["explore_speed_a"] = min(8.0, max(1.0, float(parameters["velocity_a_m_s"])))
    st.session_state["explore_speed_b"] = min(8.0, max(0.0, -float(parameters["velocity_b_m_s"])))
    st.session_state["explore_bumper_kind"] = (
        "Sticky 🧲" if float(parameters["restitution"]) == 0 else "Bouncy 🏀"
    )
    st.session_state["bumper_learning_mode"] = LearningMode.EXPLORE.value
    del st.session_state[REUSE_REQUEST_KEY]
    st.toast(f"Reused setup from Trial #{request['source_trial']}.")


def _pinned_bumper_parameters() -> CollisionParameters | None:
    notebook = get_notebook()
    if not notebook.pinned_run_a_id:
        return None
    trial = notebook.get(notebook.pinned_run_a_id)
    if trial.simulation_id != "bumper_cars":
        return None
    return CollisionParameters(**trial.parameters)


def _summary(result: CollisionResult, *, precision: int = 1) -> None:
    columns = st.columns(3)
    columns[0].metric("Car A after", f"{result.velocities_after.car_a_m_s:.{precision}f} m/s")
    columns[1].metric("Car B after", f"{result.velocities_after.car_b_m_s:.{precision}f} m/s")
    columns[2].metric(
        "Time to impact",
        f"{result.collision_time_s:.{precision}f} s"
        if result.collision_time_s is not None
        else "No impact",
    )
    st.caption(f"Text outcome: {_outcome_message(result)}")


def _diagnostics(result: CollisionResult) -> None:
    st.markdown(
        "| Measurement | Before | After |\n"
        "|---|---:|---:|\n"
        f"| Car A velocity | {result.velocities_before.car_a_m_s:.2f} m/s | {result.velocities_after.car_a_m_s:.2f} m/s |\n"
        f"| Car B velocity | {result.velocities_before.car_b_m_s:.2f} m/s | {result.velocities_after.car_b_m_s:.2f} m/s |\n"
        f"| Momentum | {result.diagnostics.momentum_before_kg_m_s:.3f} kg·m/s | "
        f"{result.diagnostics.momentum_after_kg_m_s:.3f} kg·m/s |\n"
        f"| Kinetic energy | {result.diagnostics.kinetic_energy_before_j:.3f} J | "
        f"{result.diagnostics.kinetic_energy_after_j:.3f} J |"
    )
    c1, c2 = st.columns(2)
    c1.metric("Energy lost", f"{result.diagnostics.energy_lost_j:.3f} J")
    c2.metric(
        "Center-of-mass velocity", f"{result.diagnostics.center_of_mass_velocity_m_s:.3f} m/s"
    )


def _show_canvas(result: CollisionResult) -> None:
    autoplay = st.session_state[LAUNCHED_PARAMETERS_KEY] == result.parameters.to_dict()
    document = build_bumper_canvas(
        result,
        final_message=_outcome_message(result),
        autoplay=autoplay,
        nonce=st.session_state[LAUNCH_NONCE_KEY],
    )
    canvas_kit.show(document, height=PLAYER_HEIGHT)


def _launch(result: CollisionResult, observation: str) -> None:
    if st.button(
        "💥 CRASH!", type="primary", use_container_width=True, key="bumper_explore_launch"
    ):
        if not result.collided:
            st.warning(
                "These cars won't meet. Make Car A faster than Car B, or send Car B toward Car A."
            )
            return
        next_nonce = st.session_state[LAUNCH_NONCE_KEY] + 1
        st.session_state[LAUNCHED_PARAMETERS_KEY] = result.parameters.to_dict()
        st.session_state[LAUNCH_NONCE_KEY] = next_nonce
        badges = _award_launched_missions(result)
        _record_trial(result, seed=20_260_710 + next_nonce, observation=observation, badges=badges)
        st.rerun()


def render_explore() -> None:
    mode_heading(LearningMode.EXPLORE, "Predict it, then crash it")
    revealed = kidtools.prediction_quiz(
        key="collision_quiz",
        question=(
            "Two IDENTICAL bumper cars, bouncy bumpers, no energy lost. One is zooming, "
            "one is standing still. They crash. What happens to the moving car?"
        ),
        options=[
            "It keeps going, just slower",
            "It stops completely, and the other car zooms off at its speed",
            "They both move together afterward",
        ],
        correct_index=1,
        reveal_text=(
            "It **stops dead**, and the other car shoots off at exactly the speed the first one had! "
            "With equal masses and a perfectly bouncy crash, the cars completely swap velocities."
        ),
        mission_id="collision_predict",
    )
    if not revealed:
        st.caption("🔬 The experiment unlocks after you make your guess.")
        return
    c1, c2 = st.columns(2)
    with c1:
        mass_a = st.slider("How heavy is Car A? (kg)", 0.5, 5.0, 2.0, 0.1, key="explore_mass_a")
        speed_a = st.slider(
            "How fast is Car A zooming right? (m/s)", 1.0, 8.0, 4.0, 0.1, key="explore_speed_a"
        )
    with c2:
        mass_b = st.slider("How heavy is Car B? (kg)", 0.5, 5.0, 3.0, 0.1, key="explore_mass_b")
        speed_b = st.slider(
            "Is Car B moving too? (toward Car A, m/s)", 0.0, 8.0, 0.0, 0.1, key="explore_speed_b"
        )
    kind = st.radio(
        "What kind of bumpers do they have?",
        ["Bouncy 🏀", "Sticky 🧲"],
        horizontal=True,
        key="explore_bumper_kind",
    )
    result = simulate_collision(
        CollisionParameters(
            mass_a, mass_b, speed_a, -speed_b, 0.0 if kind.startswith("Sticky") else 1.0
        )
    )
    st.markdown("#### Result summary")
    _summary(result)
    _show_canvas(result)
    observation = st.text_input(
        "Optional notebook observation",
        placeholder="What did you notice?",
        key="bumper_explore_observation",
    )
    _launch(result, observation)
    st.divider()
    kidtools.mission_checklist("Bumper Cars")


def render_compare() -> None:
    mode_heading(LearningMode.COMPARE, "Change one thing")
    st.markdown("Run A stays fixed. Build Run B by changing **one selected variable**.")
    pinned_parameters = _pinned_bumper_parameters()
    baseline_parameters = pinned_parameters or CollisionParameters(2.0, 2.0, 4.0, 0.0, 1.0)
    variable = st.selectbox("Variable to change", ["Car B mass", "Bounciness", "Car A speed"])
    if variable == "Car B mass":
        value = st.slider("Run B — Car B mass (kg)", 0.5, 5.0, 4.0, 0.1)
        modified_parameters = CollisionParameters(
            baseline_parameters.mass_a_kg,
            value,
            baseline_parameters.velocity_a_m_s,
            baseline_parameters.velocity_b_m_s,
            baseline_parameters.restitution,
        )
        change = ChangedVariable(
            variable, f"{baseline_parameters.mass_b_kg:.1f} kg", f"{value:.1f} kg"
        )
    elif variable == "Bounciness":
        value = st.slider("Run B — restitution", 0.0, 1.0, 0.5, 0.05)
        modified_parameters = CollisionParameters(
            baseline_parameters.mass_a_kg,
            baseline_parameters.mass_b_kg,
            baseline_parameters.velocity_a_m_s,
            baseline_parameters.velocity_b_m_s,
            value,
        )
        change = ChangedVariable(
            variable, f"e = {baseline_parameters.restitution:.2f}", f"e = {value:.2f}"
        )
    else:
        value = st.slider("Run B — Car A speed (m/s)", 1.0, 8.0, 6.0, 0.1)
        modified_parameters = CollisionParameters(
            baseline_parameters.mass_a_kg,
            baseline_parameters.mass_b_kg,
            value,
            baseline_parameters.velocity_b_m_s,
            baseline_parameters.restitution,
        )
        change = ChangedVariable(
            variable, f"{baseline_parameters.velocity_a_m_s:.1f} m/s", f"{value:.1f} m/s"
        )
    changed_variable_banner(change)
    col_a, col_b = st.columns(2)
    col_a.markdown(
        "#### Run A — Baseline\nPinned notebook trial"
        if pinned_parameters
        else "#### Run A — Baseline\nEqual masses, 4 m/s, perfectly bouncy"
    )
    col_b.markdown(f"#### Run B — Modified\nOnly **{variable}** changed")
    baseline = simulate_collision(baseline_parameters)
    modified = simulate_collision(modified_parameters)
    compare_observation = st.text_input(
        "Optional comparison observation",
        placeholder="What changed between A and B?",
        key="bumper_compare_observation",
    )
    signature = {
        "baseline": baseline_parameters.to_dict(),
        "modified": modified_parameters.to_dict(),
    }
    if st.button("▶ Run comparison", type="primary", use_container_width=True):
        st.session_state[COMPARE_NONCE_KEY] += 1
        st.session_state[COMPARE_SIGNATURE_KEY] = signature
        nonce = st.session_state[COMPARE_NONCE_KEY]
        _record_trial(
            baseline, seed=20_260_800 + nonce, observation=compare_observation, label="Run A"
        )
        _record_trial(
            modified, seed=20_260_900 + nonce, observation=compare_observation, label="Run B"
        )
    document = build_bumper_comparison_canvas(
        baseline,
        modified,
        changed_variable=f"{change.label}: {change.baseline} to {change.modified}",
        nonce=st.session_state[COMPARE_NONCE_KEY],
        autoplay=st.session_state[COMPARE_SIGNATURE_KEY] == signature,
    )
    canvas_kit.show(document, height=PLAYER_HEIGHT)
    comparison_metrics(comparison_measurements(baseline), comparison_measurements(modified))


def _analysis_parameters() -> CollisionParameters:
    launched = st.session_state.get(LAUNCHED_PARAMETERS_KEY)
    if launched:
        return CollisionParameters(**launched)
    return CollisionParameters(2.0, 3.0, 4.0, 0.0, 1.0)


def render_analyze() -> None:
    mode_heading(LearningMode.ANALYZE, "Measure what the collision conserved")
    result = simulate_collision(_analysis_parameters())
    st.caption(
        "Using your latest Explore trial."
        if st.session_state.get(LAUNCHED_PARAMETERS_KEY)
        else "Using the default trial until you launch one in Explore."
    )
    _summary(result, precision=2)
    st.markdown("#### Measurements and conservation diagnostics")
    _diagnostics(result)
    momentum_error = (
        result.diagnostics.momentum_after_kg_m_s - result.diagnostics.momentum_before_kg_m_s
    )
    st.success(f"Momentum check: Δp = {momentum_error:+.3e} kg·m/s")
    figure = position_figure(result.plots[0], result.collision_time_s)
    render_chart(
        figure, "Car A and Car B positions over time, with impact marked by a vertical line."
    )
    plt.close(figure)
    energy_figure = energy_retention_figure(result.parameters)
    render_chart(
        energy_figure,
        "Kinetic-energy retention increases with restitution and reaches one at a perfectly elastic collision.",
    )
    plt.close(energy_figure)
    st.markdown("#### Trial comparison")
    comparison_e = st.slider(
        "Compare latest trial with restitution e", 0.0, 1.0, 0.5, 0.05, key="analyze_e"
    )
    p = result.parameters
    comparison = simulate_collision(
        CollisionParameters(
            p.mass_a_kg, p.mass_b_kg, p.velocity_a_m_s, p.velocity_b_m_s, comparison_e
        )
    )
    comparison_metrics(comparison_measurements(result), comparison_measurements(comparison))


def render_model() -> None:
    mode_heading(LearningMode.MODEL, "The equations behind the crash")
    st.markdown("#### Equations")
    st.latex(r"m_Av_A + m_Bv_B = m_Av'_A + m_Bv'_B")
    st.latex(r"v'_B-v'_A=e(v_A-v_B)")
    st.latex(r"v'_A=v_A-\frac{(1+e)m_B(v_A-v_B)}{m_A+m_B}")
    st.latex(r"v'_B=v_B+\frac{(1+e)m_A(v_A-v_B)}{m_A+m_B}")
    assumptions = simulate_collision(CollisionParameters(2, 2, 4, 0, 1)).assumptions
    assumptions_panel(
        assumptions,
        (
            "The cars are represented as point-like bodies with a fixed visual contact distance.",
            "The collision is instantaneous; deformation happens only as an animation effect.",
            "Rotation, tire friction, steering, and two-dimensional impacts are ignored.",
            "A single restitution value summarizes all heat, sound, and deformation losses.",
        ),
    )
    with st.expander("🔧 Optional advanced controls"):
        c1, c2, c3 = st.columns(3)
        with c1:
            mass_a = st.number_input("Model mass A (kg)", 0.1, 50.0, 2.0, 0.1)
            velocity_a = st.number_input("Model velocity A (m/s)", -15.0, 15.0, 4.0, 0.1)
        with c2:
            mass_b = st.number_input("Model mass B (kg)", 0.1, 50.0, 2.0, 0.1)
            velocity_b = st.number_input("Model velocity B (m/s)", -15.0, 15.0, 0.0, 0.1)
        with c3:
            restitution = st.slider("Model restitution", 0.0, 1.0, 1.0, 0.05)
        result = simulate_collision(
            CollisionParameters(mass_a, mass_b, velocity_a, velocity_b, restitution)
        )
        if result.collided:
            _summary(result, precision=2)
            _diagnostics(result)
        else:
            st.warning("This setup never collides because Car A does not catch Car B.")


def render() -> None:
    _initialize_state()
    _apply_reuse_request()
    st.header("🚗 Bumper Cars")
    st.markdown(
        "Two cars, one track, one crash—explore it, compare trials, analyze the evidence, or inspect the model."
    )
    mode = mode_navigation(key="bumper_learning_mode")
    st.divider()
    try:
        if mode is LearningMode.EXPLORE:
            render_explore()
        elif mode is LearningMode.COMPARE:
            render_compare()
        elif mode is LearningMode.ANALYZE:
            render_analyze()
        else:
            render_model()
    except PhysicsValidationError as error:
        st.error(f"That setup can't run yet: {error}")
