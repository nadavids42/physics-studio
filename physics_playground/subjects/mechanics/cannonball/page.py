"""Four-mode Cannonball Launcher page."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import streamlit as st

from physics_playground.canvas import embed as canvas_embed
from physics_playground.contracts import JsonValue, MissionEvaluation, SummaryMetric
from physics_playground.missions import ui as mission_ui
from physics_playground.model_metadata import PROJECTILE_MODEL_METADATA
from physics_playground.presentation.learning_modes import (
    LearningMode,
    assumptions_panel,
    changed_variable_banner,
    comparison_metrics,
    mode_heading,
    mode_navigation,
    result_summary,
    run_model_safely,
)
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.setup_handoff import consume_setup_request
from physics_playground.simulation_cache import cached_projectile
from physics_playground.state_keys import SHARED_STATE_KEYS, migrate_simulation_keys, simulation_key
from physics_playground.subjects.mechanics.cannonball.interactions import (
    comparison_results,
    notebook_metrics,
    target_for_seed,
    target_message,
)
from physics_playground.subjects.mechanics.cannonball.lesson import CANNONBALL_LESSON
from physics_playground.subjects.mechanics.cannonball.linked_representations import (
    LINKED_HEIGHT,
    build_linked_projectile_document,
)
from physics_playground.subjects.mechanics.cannonball.missions import evaluate_cannonball_missions
from physics_playground.subjects.mechanics.cannonball.physics import (
    PROJECTILE_MODEL_VERSION,
    ProjectileParameters,
    ProjectileResult,
)
from physics_playground.subjects.mechanics.cannonball.scene import (
    PLAYER_HEIGHT,
    build_cannon_canvas,
)
from physics_playground.units import (
    EARTH_GRAVITY_M_S2,
    JUPITER_GRAVITY_M_S2,
    MOON_GRAVITY_M_S2,
)

ID = "cannonball"

WORLDS = {
    "Earth 🌍": EARTH_GRAVITY_M_S2,
    "The Moon 🌕": MOON_GRAVITY_M_S2,
    "Jupiter 🟠": JUPITER_GRAVITY_M_S2,
}

SUMMARY_METRIC_IDS = {"range", "maximum_height", "flight_time"}


def state_key(name: str) -> str:
    canonical = simulation_key(ID, name)
    if name in st.session_state and canonical not in st.session_state:
        st.session_state[canonical] = st.session_state.pop(name)
    return canonical


def summary_metrics(result: ProjectileResult) -> tuple[SummaryMetric, ...]:
    return tuple(metric for metric in result.metrics if metric.id in SUMMARY_METRIC_IDS)


def accessible_summary(result: ProjectileResult) -> str:
    landing = "landed" if result.landed else "did not land"
    return (
        f"The projectile {landing} after traveling {result.range_m:.1f} meters horizontally "
        f"and reaching {result.maximum_height_m:.1f} meters high."
    )


def mission_evidence(
    result: ProjectileResult, context: Mapping[str, JsonValue]
) -> tuple[MissionEvaluation, ...]:
    target = context.get("target_m")
    if not isinstance(target, int | float):
        return ()
    return cast(
        tuple[MissionEvaluation, ...],
        evaluate_cannonball_missions(result, float(target)),
    )


def _init() -> None:
    migrate_simulation_keys(
        st.session_state,
        ID,
        {
            "cannon_target_seed": "target_seed",
            "cannon_target_override": "target_override",
            "cannon_speed": "speed",
            "cannon_angle": "angle",
            "cannon_world": "world",
            "cannon_learning_mode": "learning_mode",
            "cannon_quiz_guess": "quiz_guess",
            "cannon_reuse_target": "reuse_target",
            "cannon_observation": "observation",
            "cannon_compare_observation": "compare_observation",
        },
        removal_condition=(
            "the documented compatibility release has elapsed and persisted-session fixtures "
            "contain only physics_studio.simulation.cannonball keys"
        ),
    )
    st.session_state.setdefault(state_key("target_seed"), 20260710)
    st.session_state.setdefault(state_key("launch_nonce"), 0)
    st.session_state.setdefault(state_key("launched_parameters"), None)
    st.session_state.setdefault(state_key("compare_nonce"), 0)
    st.session_state.setdefault(state_key("compare_signature"), None)
    st.session_state.setdefault(state_key("target_override"), None)


def _target() -> float:
    if st.session_state[state_key("target_override")] is not None:
        return float(st.session_state[state_key("target_override")])
    return target_for_seed(int(st.session_state[state_key("target_seed")]))


def _new_target() -> None:
    st.session_state[state_key("target_override")] = None
    st.session_state[state_key("target_seed")] += 1


def _apply_reuse() -> None:
    request = consume_setup_request(st.session_state, "cannonball")
    if request is None:
        return
    p = request.parameters
    st.session_state[state_key("speed")] = min(40.0, max(5.0, float(p["launch_speed_m_s"])))
    st.session_state[state_key("angle")] = min(89, max(5, int(round(float(p["launch_angle_deg"])))))
    gravity = float(p["gravity_m_s2"])
    st.session_state[state_key("world")] = min(
        WORLDS, key=lambda label: abs(WORLDS[label] - gravity)
    )
    st.session_state[state_key("target_override")] = float(p.get("target_m", _target()))
    st.session_state[state_key("learning_mode")] = LearningMode.EXPLORE.value
    st.toast(f"Loaded setup from {request.source_label}.")


def _start_guided_lesson() -> None:
    st.session_state[SHARED_STATE_KEYS.navigation_active_lesson] = CANNONBALL_LESSON.id
    st.query_params["simulation"] = ID
    st.query_params["lesson"] = CANNONBALL_LESSON.id


def _execute(parameters: ProjectileParameters) -> ProjectileResult:
    """Run through shared error handling; stop this mode after a reported failure."""

    result = run_model_safely(lambda: cast(ProjectileResult, cached_projectile(parameters)))
    if result is None:
        st.stop()
    return result


def _record_result(
    result: ProjectileResult,
    target: float,
    seed: int,
    observation: str,
    label: str | None = None,
    badges: tuple[str, ...] = (),
) -> None:
    prediction = st.session_state.get(state_key("quiz_guess"))
    add_trial(
        simulation_id=ID,
        parameters=result.parameters.to_dict(),
        prediction=prediction if isinstance(prediction, str) else None,
        result_summary=target_message(result, target),
        metrics=notebook_metrics(result),
        earned_badges=badges,
        random_seed=seed,
        model_version=PROJECTILE_MODEL_VERSION,
        learner_observation=observation,
        label=label,
    )


@st.fragment
def _explore_commit_controls(result: ProjectileResult, target: float, same_target: bool) -> None:
    """Update notes independently so typing does not remount the player iframe."""

    observation = st.text_input(
        "Optional notebook observation",
        placeholder="What did you notice?",
        key=state_key("observation"),
    )
    if st.button("💥 FIRE!", type="primary", use_container_width=True):
        nonce = st.session_state[state_key("launch_nonce")] + 1
        st.session_state[state_key("launch_nonce")] = nonce
        st.session_state[state_key("launched_parameters")] = result.parameters.to_dict()
        badges = mission_ui.process_run(ID, mission_evidence(result, {"target_m": target}))
        _record_result(
            result,
            target,
            st.session_state[state_key("target_seed")],
            observation,
            badges=badges,
        )
        if not same_target:
            st.session_state[state_key("target_override")] = None
            st.session_state[state_key("target_seed")] += 1
        st.rerun(scope="app")


def render_explore() -> None:
    mode_heading(LearningMode.EXPLORE, "Aim, predict, and fire")
    with st.form(state_key("setup_form"), border=True):
        st.markdown("**Configure the next launch**")
        c1, c2 = st.columns(2)
        with c1:
            speed = st.slider("Launch speed (m/s)", 5.0, 40.0, 20.0, 0.5, key=state_key("speed"))
        with c2:
            angle = st.slider("Launch angle (degrees)", 5, 89, 45, 1, key=state_key("angle"))
        world = st.radio("World", list(WORLDS), horizontal=True, key=state_key("world"))
        st.form_submit_button("Apply launch setup", type="primary", use_container_width=True)
    gravity = WORLDS[world]
    same = st.checkbox("Reuse the same target", value=True, key=state_key("reuse_target"))
    st.button("🔄 New deterministic target", disabled=same, on_click=_new_target)
    target = _target()
    st.info(f"🎯 Target: {target:.1f} m")
    parameters = ProjectileParameters(speed, angle, gravity)
    result = run_model_safely(lambda: cast(ProjectileResult, cached_projectile(parameters)))
    if result is None:
        return
    result_summary(summary_metrics(result))
    st.caption("Text outcome: " + accessible_summary(result))
    autoplay = st.session_state[state_key("launched_parameters")] == result.parameters.to_dict()
    doc = build_cannon_canvas(
        result,
        target_m=target,
        message=target_message(result, target),
        seed=st.session_state[state_key("target_seed")],
        autoplay=autoplay,
    )
    canvas_embed.show(doc, height=PLAYER_HEIGHT)
    _explore_commit_controls(result, target, same)
    mission_ui.mission_checklist("Cannonball Launcher")


@st.fragment
def _compare_commit_controls(
    first: ProjectileResult,
    second: ProjectileResult,
    target: float,
    signature: dict[str, object],
) -> None:
    observation = st.text_input(
        "Optional comparison observation", key=state_key("compare_observation")
    )
    if st.button("▶ Run comparison", type="primary", use_container_width=True):
        st.session_state[state_key("compare_nonce")] += 1
        st.session_state[state_key("compare_signature")] = signature
        nonce = st.session_state[state_key("compare_nonce")]
        _record_result(first, target, 20260800 + nonce, observation, "Run A")
        _record_result(second, target, 20260900 + nonce, observation, "Run B")
        st.rerun(scope="app")


def render_compare() -> None:
    mode_heading(LearningMode.COMPARE, "Overlay two trajectories")
    kind = st.selectbox(
        "Comparison", ["30° versus 60°", "With drag versus without drag", "Earth versus Moon"]
    )
    a, b, labels, change = comparison_results(kind, _execute)
    changed_variable_banner(change)
    target = _target()
    signature = {"kind": kind, "seed": st.session_state[state_key("target_seed")]}
    doc = build_linked_projectile_document(((labels[0], a), (labels[1], b)), target_m=target)
    canvas_embed.show(doc, height=LINKED_HEIGHT)
    _compare_commit_controls(a, b, target, signature)
    comparison_metrics(
        {key: (key, value) for key, value in notebook_metrics(a).items()},
        {key: (key, value) for key, value in notebook_metrics(b).items()},
    )


def _latest() -> ProjectileParameters:
    saved = st.session_state.get(state_key("launched_parameters"))
    return (
        ProjectileParameters(**saved) if saved else ProjectileParameters(25, 40, EARTH_GRAVITY_M_S2)
    )


def render_analyze() -> None:
    mode_heading(LearningMode.ANALYZE, "Inspect the flight data")
    base = _latest()
    drag = st.slider("Analysis drag coefficient", 0.0, 0.3, base.drag_coefficient_kg_m, 0.01)
    result = _execute(
        ProjectileParameters(
            base.launch_speed_m_s,
            base.launch_angle_deg,
            base.gravity_m_s2,
            base.initial_height_m,
            base.mass_kg,
            drag,
            base.time_step_s,
            base.max_time_s,
            base.samples,
        )
    )
    if not result.landed:
        st.warning(result.warnings[0])
    result_summary(summary_metrics(result))
    st.caption("Text outcome: " + accessible_summary(result))
    st.caption(
        "Linked representation proof: animation, trajectory, component graphs, acceleration, "
        "and equations share one browser-side time state. No Streamlit rerun is needed to scrub."
    )
    canvas_embed.show(
        build_linked_projectile_document((("Current run", result),), target_m=_target()),
        height=LINKED_HEIGHT,
    )


def render_model() -> None:
    mode_heading(LearningMode.MODEL, "Equations, assumptions, and numerical methods")
    st.markdown("#### No-drag analytic model")
    st.latex(r"x(t)=v_0\cos(\theta)t")
    st.latex(r"y(t)=y_0+v_0\sin(\theta)t-\frac12gt^2")
    st.latex(r"R=\frac{v_0^2\sin(2\theta)}{g}\quad(y_0=0)")
    st.markdown("#### Quadratic-drag numerical model")
    st.latex(r"\vec F_d=-k|\vec v|\vec v")
    st.markdown(
        "The drag model uses fixed-step fourth-order Runge–Kutta (RK4). When a step crosses the ground, the final state and time are linearly interpolated to **exactly y = 0**, avoiding range overshoot from simple clamping."
    )
    assumptions_panel(PROJECTILE_MODEL_METADATA.assumptions, PROJECTILE_MODEL_METADATA.limitations)
    with st.expander("🔧 Optional advanced controls"):
        c1, c2, c3 = st.columns(3)
        with c1:
            speed = st.number_input("Model speed", 1.0, 100.0, 25.0)
            angle = st.number_input("Model angle", 1.0, 89.0, 40.0)
        with c2:
            mass = st.number_input("Mass (kg)", 0.1, 50.0, 5.0)
            drag = st.number_input("Drag k", 0.0, 2.0, 0.05, 0.01)
        with c3:
            dt = st.number_input("Time step (s)", 0.0005, 0.1, 0.005, 0.0005, format="%.4f")
            limit = st.number_input("Maximum time (s)", 1.0, 300.0, 120.0)
        result = _execute(
            ProjectileParameters(
                speed,
                angle,
                EARTH_GRAVITY_M_S2,
                mass_kg=mass,
                drag_coefficient_kg_m=drag,
                time_step_s=dt,
                max_time_s=limit,
            )
        )
        result_summary(summary_metrics(result))
        st.caption("Text outcome: " + accessible_summary(result))
        if not result.landed:
            st.error(
                "The projectile did not land before the maximum-time limit. Increase the limit or inspect the setup."
            )


def render() -> None:
    _init()
    _apply_reuse()
    st.header("Cannonball Launcher — Projectile Motion")
    st.markdown(
        "Launch a cannonball, compare trajectories, analyze the measurements, or inspect the model."
    )
    lesson_active = st.session_state.get(SHARED_STATE_KEYS.navigation_active_lesson) is not None
    if not lesson_active:
        st.info(
            "You are using the standalone simulation. The guided lesson is available separately "
            "and does not restrict direct access to simulation modes."
        )
        st.button("Start guided lesson", on_click=_start_guided_lesson)
        revealed = mission_ui.prediction_quiz(
            key=state_key("quiz"),
            question="For maximum no-drag range on level ground, which angle wins?",
            options=["15°", "45°", "75°", "90°"],
            correct_index=1,
            reveal_text="**45 degrees** balances horizontal speed and time aloft.",
            mission_id="cannon_predict",
        )
        if not revealed:
            st.caption("🔬 Make your prediction before any results are shown.")
            return
    mode = mode_navigation(key=state_key("learning_mode"))
    st.divider()
    {
        LearningMode.EXPLORE: render_explore,
        LearningMode.COMPARE: render_compare,
        LearningMode.ANALYZE: render_analyze,
        LearningMode.MODEL: render_model,
    }[mode]()
