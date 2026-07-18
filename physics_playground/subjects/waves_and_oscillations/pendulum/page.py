"""Four-mode Swing Machine page."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import embed as canvas_embed
from physics_playground.missions import ui as mission_ui
from physics_playground.presentation.accessibility_ui import render_chart
from physics_playground.presentation.learning_modes import (
    ChangedVariable,
    LearningMode,
    assumptions_panel,
    changed_variable_banner,
    comparison_metrics,
    mode_heading,
    mode_navigation,
)
from physics_playground.presentation.notebook_ui import REUSE_REQUEST_KEY, add_trial
from physics_playground.simulation_cache import cached_pendulum
from physics_playground.state_keys import migrate_simulation_keys, simulation_key
from physics_playground.subjects.waves_and_oscillations.pendulum.charts import (
    error_figure,
    plot_figure,
)
from physics_playground.subjects.waves_and_oscillations.pendulum.missions import (
    evaluate_pendulum_missions,
)
from physics_playground.subjects.waves_and_oscillations.pendulum.physics import (
    PendulumModel,
    PendulumParameters,
    nonlinear_period_series,
)
from physics_playground.subjects.waves_and_oscillations.pendulum.scene import (
    PLAYER_HEIGHT,
    build_pendulum_canvas,
    build_pendulum_comparison_canvas,
)
from physics_playground.units import (
    EARTH_GRAVITY_M_S2,
    JUPITER_GRAVITY_M_S2,
    MOON_GRAVITY_M_S2,
)
from physics_playground.validation import PhysicsValidationError

WORLDS = {
    "Earth 🌍": EARTH_GRAVITY_M_S2,
    "The Moon 🌕": MOON_GRAVITY_M_S2,
    "Jupiter 🟠": JUPITER_GRAVITY_M_S2,
}
VERSION = "pendulum-2.0"
ID = "pendulum"


def state_key(name: str) -> str:
    return simulation_key(ID, name)


def _init():
    migrate_simulation_keys(
        st.session_state,
        ID,
        {
            "pend_nonce": "nonce",
            "pend_launched": "launched",
            "pend_compare_nonce": "compare_nonce",
            "pend_compare_signature": "compare_signature",
            "pend_length": "length",
            "pend_angle": "angle",
            "pend_model": "model",
            "pend_world": "world",
            "pend_learning_mode": "learning_mode",
            "pend_quiz_guess": "quiz_guess",
            "pend_quiz_revealed": "quiz_revealed",
            "pend_quiz_lock": "quiz_lock",
            "pend_observation": "observation",
            "pend_compare_observation": "compare_observation",
        },
    )
    for k, v in (
        (state_key("nonce"), 0),
        (state_key("launched"), None),
        (state_key("compare_nonce"), 0),
        (state_key("compare_signature"), None),
    ):
        st.session_state.setdefault(k, v)


def _summary(r):
    c = st.columns(3)
    c[0].metric("Period", f"{r.period_s:.2f} s")
    c[1].metric("Top speed", f"{r.maximum_speed_m_s:.2f} m/s")
    c[2].metric("Energy drift", f"{r.energy_drift_fraction * 100:.4f}%")
    st.caption(
        f"Text outcome: this {r.parameters.model.value.lower()} swing has a {r.period_s:.2f}-second period and reaches {r.maximum_speed_m_s:.2f} meters per second."
    )


def _metrics(r):
    return {
        "period_s": r.period_s,
        "maximum_speed_m_s": r.maximum_speed_m_s,
        "energy_drift_percent": r.energy_drift_fraction * 100,
    }


def _record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id="pendulum",
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("quiz_guess")),
        result_summary=f"{r.parameters.model.value}: period {r.period_s:.2f} s",
        metrics=_metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def _award(r):
    return mission_ui.process_run("pendulum", evaluate_pendulum_missions(r))


def _reuse():
    q = st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id") != "pendulum":
        return
    p = q["parameters"]
    st.session_state[state_key("length")] = float(p["length_m"])
    st.session_state[state_key("angle")] = int(round(float(p["release_angle_deg"])))
    st.session_state[state_key("model")] = p["model"]
    st.session_state[state_key("world")] = min(
        WORLDS, key=lambda x: abs(WORLDS[x] - float(p["gravity_m_s2"]))
    )
    st.session_state[state_key("learning_mode")] = "Explore"
    del st.session_state[REUSE_REQUEST_KEY]


def render_explore():
    mode_heading(LearningMode.EXPLORE, "Choose a rope, world, and model")
    c1, c2 = st.columns(2)
    with c1:
        length = st.slider("Rope length (m)", 0.2, 10.0, 2.0, 0.1, key=state_key("length"))
        angle = st.slider("Release angle (degrees)", 5, 85, 30, 1, key=state_key("angle"))
    with c2:
        world = st.radio("World", list(WORLDS), key=state_key("world"))
        model = PendulumModel(
            st.radio("Physics model", [m.value for m in PendulumModel], key=state_key("model"))
        )
    r = cached_pendulum(PendulumParameters(length, WORLDS[world], angle, model))
    _summary(r)
    if model is PendulumModel.SMALL_ANGLE:
        reference_period = nonlinear_period_series(length, WORLDS[world], angle)
        error_percent = (reference_period / r.period_s - 1) * 100
        message = (
            f"Small-angle model: sin(θ) is replaced by θ. At {angle}°, its period is about "
            f"{error_percent:.1f}% shorter than the nonlinear period estimate."
        )
        if angle > 15:
            st.warning(message + " Use the nonlinear model for quantitative interpretation.")
        else:
            st.caption(message)
    autoplay = st.session_state[state_key("launched")] == r.parameters.to_dict()
    canvas_embed.show(
        build_pendulum_canvas(
            r, seed=20261500 + st.session_state[state_key("nonce")], autoplay=autoplay
        ),
        height=PLAYER_HEIGHT,
    )
    obs = st.text_input("Optional notebook observation", key=state_key("observation"))
    if st.button("🎢 SWING!", type="primary", use_container_width=True):
        st.session_state[state_key("nonce")] += 1
        st.session_state[state_key("launched")] = r.parameters.to_dict()
        badges = _award(r)
        _record(r, 20261500 + st.session_state[state_key("nonce")], obs, badges=badges)
        st.rerun()
    mission_ui.mission_checklist("The Swing Machine")


def _pair(kind):
    if kind == "Short versus long pendulum":
        a = PendulumParameters(1, EARTH_GRAVITY_M_S2, 30)
        b = PendulumParameters(5, EARTH_GRAVITY_M_S2, 30)
        change = ChangedVariable("Length", "1 m", "5 m")
        labels = ("Short", "Long")
    elif kind == "Earth versus Moon":
        a = PendulumParameters(2, EARTH_GRAVITY_M_S2, 30)
        b = PendulumParameters(2, MOON_GRAVITY_M_S2, 30)
        change = ChangedVariable("Gravity", "Earth", "Moon")
        labels = ("Earth", "Moon")
    elif kind == "Small versus large release angle":
        a = PendulumParameters(2, EARTH_GRAVITY_M_S2, 10, PendulumModel.NONLINEAR)
        b = PendulumParameters(2, EARTH_GRAVITY_M_S2, 75, PendulumModel.NONLINEAR)
        change = ChangedVariable("Release angle", "10°", "75°")
        labels = ("Small angle", "Large angle")
    else:
        a = PendulumParameters(2, EARTH_GRAVITY_M_S2, 70, PendulumModel.SMALL_ANGLE)
        b = PendulumParameters(2, EARTH_GRAVITY_M_S2, 70, PendulumModel.NONLINEAR)
        change = ChangedVariable("Model", "Small-angle", "Nonlinear")
        labels = ("Approximation", "Nonlinear")
    return cached_pendulum(a), cached_pendulum(b), labels, change


def render_compare():
    mode_heading(LearningMode.COMPARE, "Overlay pendulum trials")
    kind = st.selectbox(
        "Comparison",
        [
            "Short versus long pendulum",
            "Earth versus Moon",
            "Small versus large release angle",
            "Small-angle versus nonlinear model",
        ],
    )
    a, b, labels, change = _pair(kind)
    changed_variable_banner(change)
    sig = {"kind": kind}
    obs = st.text_input("Optional comparison observation", key=state_key("compare_observation"))
    if st.button("▶ Run comparison", type="primary", use_container_width=True):
        st.session_state[state_key("compare_nonce")] += 1
        st.session_state[state_key("compare_signature")] = sig
        n = st.session_state[state_key("compare_nonce")]
        _record(a, 20261600 + n, obs, "Run A")
        _record(b, 20261700 + n, obs, "Run B")
    canvas_embed.show(
        build_pendulum_comparison_canvas(
            a,
            b,
            labels=labels,
            seed=20261800 + st.session_state[state_key("compare_nonce")],
            autoplay=st.session_state[state_key("compare_signature")] == sig,
        ),
        height=PLAYER_HEIGHT,
    )
    comparison_metrics(
        {k: (k, v) for k, v in _metrics(a).items()}, {k: (k, v) for k, v in _metrics(b).items()}
    )


def _latest():
    if not st.session_state[state_key("launched")]:
        return PendulumParameters(2, EARTH_GRAVITY_M_S2, 30, PendulumModel.NONLINEAR)
    d = dict(st.session_state[state_key("launched")])
    d["model"] = PendulumModel(d["model"])
    return PendulumParameters(**d)


def render_analyze():
    mode_heading(LearningMode.ANALYZE, "Inspect angle, energy, and phase space")
    p = _latest()
    r = cached_pendulum(p)
    _summary(r)
    for plot in r.plots:
        fig = plot_figure(plot)
        render_chart(fig, f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.")
        plt.close(fig)
    fig = error_figure(p.length_m, p.gravity_m_s2)
    render_chart(fig, "Approximation error increases as release angle grows.")
    plt.close(fig)


def render_model():
    mode_heading(LearningMode.MODEL, "Approximation versus nonlinear motion")
    st.latex(r"\ddot\theta+\frac{g}{L}\sin\theta=0")
    st.latex(r"\sin\theta\approx\theta\Rightarrow T_0=2\pi\sqrt{L/g}")
    st.markdown(
        "The small-angle model is analytical. The nonlinear equation is integrated with RK4; its period grows with release angle."
    )
    assumptions = cached_pendulum(PendulumParameters(2, EARTH_GRAVITY_M_S2, 30)).assumptions
    assumptions_panel(
        assumptions,
        (
            "Air drag and pivot friction are omitted.",
            "The bob has no physical size or rotation.",
            "The support and local gravity remain fixed.",
            "The large-angle period display uses a truncated series.",
        ),
    )
    with st.expander("🔧 Optional advanced controls"):
        length = st.number_input("Advanced length", 0.1, 20.0, 2.0)
        gravity = st.number_input("Advanced gravity", 0.1, 30.0, EARTH_GRAVITY_M_S2)
        angle = st.number_input("Advanced angle", 1.0, 170.0, 60.0)
        model = PendulumModel(st.selectbox("Advanced model", [m.value for m in PendulumModel]))
        _summary(cached_pendulum(PendulumParameters(length, gravity, angle, model)))


def render():
    _init()
    _reuse()
    st.header("🎢 The Swing Machine")
    st.markdown("Explore how length, gravity, angle, and model choice change a pendulum.")
    revealed = mission_ui.prediction_quiz(
        key=state_key("quiz"),
        question="If you pull a small-angle swing farther, one full swing takes...",
        options=["More time", "Less time", "Almost exactly the same time"],
        correct_index=2,
        reveal_text="For small angles, period depends on length and gravity, not amplitude.",
        mission_id="pend_predict",
    )
    if not revealed:
        st.caption("🔬 Make your prediction before results are shown.")
        return
    mode = mode_navigation(key=state_key("learning_mode"))
    st.divider()
    try:
        {
            LearningMode.EXPLORE: render_explore,
            LearningMode.COMPARE: render_compare,
            LearningMode.ANALYZE: render_analyze,
            LearningMode.MODEL: render_model,
        }[mode]()
    except PhysicsValidationError as e:
        st.error(f"That setup can't run yet: {e}")
