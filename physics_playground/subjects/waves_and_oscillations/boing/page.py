"""Four-mode Boing Machine page."""

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
from physics_playground.simulation_cache import cached_spring
from physics_playground.state_keys import migrate_simulation_keys, simulation_key
from physics_playground.subjects.waves_and_oscillations.boing.charts import (
    plot_figure,
    resonance_figure,
)
from physics_playground.subjects.waves_and_oscillations.boing.missions import (
    evaluate_boing_missions,
)
from physics_playground.subjects.waves_and_oscillations.boing.physics import (
    SpringParameters,
    SpringResult,
)
from physics_playground.subjects.waves_and_oscillations.boing.scene import (
    PLAYER_HEIGHT,
    build_boing_canvas,
    build_boing_comparison_canvas,
)
from physics_playground.validation import PhysicsValidationError

MODEL_VERSION = "spring-2.0"
ID = "boing"
PRESETS = {"Half natural frequency": 0.5, "Natural frequency": 1.0, "Twice natural frequency": 2.0}


def state_key(name: str) -> str:
    return simulation_key(ID, name)


def _init():
    migrate_simulation_keys(
        st.session_state,
        ID,
        {
            "spring_nonce": "nonce",
            "spring_launched": "launched",
            "spring_compare_nonce": "compare_nonce",
            "spring_compare_signature": "compare_signature",
            "spring_quiz_guess": "quiz_guess",
            "spring_quiz_revealed": "quiz_revealed",
            "spring_quiz_lock": "quiz_lock",
            "boing_mass": "mass",
            "boing_k": "stiffness",
            "boing_amp": "amplitude",
            "boing_learning_mode": "learning_mode",
            "boing_observation": "observation",
            "boing_compare_observation": "compare_observation",
        },
    )
    for key, value in (
        (state_key("nonce"), 0),
        (state_key("launched"), None),
        (state_key("compare_nonce"), 0),
        (state_key("compare_signature"), None),
    ):
        st.session_state.setdefault(key, value)


def _summary(r: SpringResult):
    c = st.columns(3)
    c[0].metric("Natural frequency", f"{r.natural_frequency_hz:.3f} Hz")
    c[1].metric("Angular frequency", f"{r.natural_angular_frequency_rad_s:.2f} rad/s")
    c[2].metric("Period", f"{r.period_s:.2f} s")
    st.caption(
        f"Text outcome: the oscillator's natural period is {r.period_s:.2f} seconds and its late response amplitude is {r.late_response_amplitude_m:.2f} meters."
    )


def _metrics(r):
    return {
        "period_s": r.period_s,
        "natural_frequency_hz": r.natural_frequency_hz,
        "maximum_speed_m_s": r.maximum_speed_m_s,
        "late_amplitude_m": r.late_response_amplitude_m,
    }


def _record(r, seed, observation, label=None, badges=()):
    add_trial(
        simulation_id="boing",
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("quiz_guess")),
        result_summary=f"Period {r.period_s:.2f} s; late amplitude {r.late_response_amplitude_m:.2f} m",
        metrics=_metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=MODEL_VERSION,
        learner_observation=observation,
        label=label,
    )


def _award(r):
    return mission_ui.process_run("boing", evaluate_boing_missions(r))


def _reuse():
    q = st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id") != "boing":
        return
    p = q["parameters"]
    for key, name in (
        (state_key("mass"), "mass_kg"),
        (state_key("stiffness"), "stiffness_n_m"),
        (state_key("amplitude"), "initial_displacement_m"),
    ):
        st.session_state[key] = float(p[name])
    st.session_state[state_key("learning_mode")] = "Explore"
    del st.session_state[REUSE_REQUEST_KEY]
    st.toast(f"Reused setup from Trial #{q['source_trial']}.")


def render_explore():
    mode_heading(LearningMode.EXPLORE, "Build it and make it boing")
    c1, c2 = st.columns(2)
    with c1:
        mass = st.slider("Mass (kg)", 0.2, 10.0, 2.0, 0.1, key=state_key("mass"))
        k = st.slider("Spring stiffness (N/m)", 1.0, 100.0, 20.0, 1.0, key=state_key("stiffness"))
    with c2:
        amp = st.slider("Starting pull (m)", 0.2, 2.0, 1.0, 0.1, key=state_key("amplitude"))
        preset = st.selectbox("Driving preset", ["No driving", *PRESETS])
    drive = 0.0 if preset == "No driving" else st.slider("Driving force (N)", 0.5, 10.0, 4.0, 0.5)
    ratio = 1.0 if preset == "No driving" else PRESETS[preset]
    damping = 0.0 if preset == "No driving" else st.slider("Damping (N·s/m)", 0.0, 3.0, 0.3, 0.1)
    r = cached_spring(SpringParameters(mass, k, amp, damping, drive, ratio, 20, 600))
    _summary(r)
    autoplay = st.session_state[state_key("launched")] == r.parameters.to_dict()
    canvas_embed.show(
        build_boing_canvas(
            r, seed=20261100 + st.session_state[state_key("nonce")], autoplay=autoplay
        ),
        height=PLAYER_HEIGHT,
    )
    observation = st.text_input("Optional notebook observation", key=state_key("observation"))
    if st.button("🌀 BOING!", type="primary", use_container_width=True):
        st.session_state[state_key("nonce")] += 1
        st.session_state[state_key("launched")] = r.parameters.to_dict()
        badges = _award(r)
        _record(r, 20261100 + st.session_state[state_key("nonce")], observation, badges=badges)
        st.rerun()
    mission_ui.mission_checklist("Boing Machine")


def _compare(kind):
    base = SpringParameters(2, 20, 1, duration_s=20, samples=600)
    if kind == "Light versus heavy mass":
        return (
            cached_spring(SpringParameters(0.7, 20, 1, duration_s=20, samples=600)),
            cached_spring(SpringParameters(5, 20, 1, duration_s=20, samples=600)),
            ("Light", "Heavy"),
            ChangedVariable("Mass", "0.7 kg", "5.0 kg"),
        )
    if kind == "Soft versus stiff spring":
        return (
            cached_spring(SpringParameters(2, 6, 1, duration_s=20, samples=600)),
            cached_spring(SpringParameters(2, 60, 1, duration_s=20, samples=600)),
            ("Soft", "Stiff"),
            ChangedVariable("Stiffness", "6 N/m", "60 N/m"),
        )
    if kind == "Damped versus undamped":
        return (
            cached_spring(base),
            cached_spring(SpringParameters(2, 20, 1, 1.2, duration_s=20, samples=600)),
            ("Undamped", "Damped"),
            ChangedVariable("Damping", "0", "1.2 N·s/m"),
        )
    return (
        cached_spring(SpringParameters(2, 20, 0.1, 0.3, 4, 0.5, 30, 900)),
        cached_spring(SpringParameters(2, 20, 0.1, 0.3, 4, 1, 30, 900)),
        ("Half-frequency", "Resonant"),
        ChangedVariable("Drive frequency", "0.5× natural", "1.0× natural"),
    )


def render_compare():
    mode_heading(LearningMode.COMPARE, "Change one oscillator property")
    kind = st.selectbox(
        "Comparison",
        [
            "Light versus heavy mass",
            "Soft versus stiff spring",
            "Damped versus undamped",
            "Resonant versus non-resonant driving",
        ],
    )
    a, b, labels, change = _compare(kind)
    changed_variable_banner(change)
    signature = {"kind": kind}
    obs = st.text_input("Optional comparison observation", key=state_key("compare_observation"))
    if st.button("▶ Run comparison", type="primary", use_container_width=True):
        st.session_state[state_key("compare_nonce")] += 1
        st.session_state[state_key("compare_signature")] = signature
        n = st.session_state[state_key("compare_nonce")]
        _record(a, 20261200 + n, obs, "Run A")
        _record(b, 20261300 + n, obs, "Run B")
    canvas_embed.show(
        build_boing_comparison_canvas(
            a,
            b,
            labels=labels,
            seed=20261400 + st.session_state[state_key("compare_nonce")],
            autoplay=st.session_state[state_key("compare_signature")] == signature,
        ),
        height=PLAYER_HEIGHT,
    )
    comparison_metrics(
        {k: (k, v) for k, v in _metrics(a).items()}, {k: (k, v) for k, v in _metrics(b).items()}
    )


def _latest():
    return (
        SpringParameters(**st.session_state[state_key("launched")])
        if st.session_state[state_key("launched")]
        else SpringParameters(2, 20, 1, duration_s=20, samples=600)
    )


def render_analyze():
    mode_heading(LearningMode.ANALYZE, "Measure motion, energy, and resonance")
    r = cached_spring(_latest())
    _summary(r)
    for plot in r.plots:
        fig = plot_figure(plot)
        render_chart(fig, f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.")
        plt.close(fig)
    fig = resonance_figure(
        r.parameters.mass_kg,
        r.parameters.stiffness_n_m,
        max(0.15, r.parameters.damping_n_s_m),
        max(4, r.parameters.drive_force_n),
    )
    render_chart(
        fig, "Response amplitude versus driving-frequency ratio, with natural frequency marked."
    )
    plt.close(fig)


def render_model():
    mode_heading(LearningMode.MODEL, "The oscillator equation")
    st.latex(r"m\ddot x+c\dot x+kx=F_0\cos(\omega_dt)")
    st.latex(r"\omega_0=\sqrt{k/m},\quad T=2\pi\sqrt{m/k}")
    st.markdown(
        "Ideal undamped motion is analytical. Damped and driven motion uses fixed-step RK4. The resonance sweep is cached by its physical parameters."
    )
    assumptions = cached_spring(SpringParameters(2, 20, 1)).assumptions
    assumptions_panel(
        assumptions,
        (
            "Real springs become nonlinear at large stretch.",
            "Spring mass and internal friction are omitted.",
            "The support does not move unless represented by the sinusoidal drive.",
            "The displayed late amplitude is a finite-window estimate.",
        ),
    )
    with st.expander("🔧 Optional advanced controls"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.number_input("Advanced mass", 0.1, 20.0, 2.0)
            k = st.number_input("Advanced stiffness", 0.5, 200.0, 20.0)
        with c2:
            d = st.number_input("Advanced damping", 0.0, 10.0, 0.3, 0.1)
            f = st.number_input("Drive force", 0.0, 20.0, 4.0, 0.5)
        with c3:
            preset = st.selectbox("Drive frequency preset", list(PRESETS))
            ratio = PRESETS[preset]
        r = cached_spring(SpringParameters(m, k, 0.1, d, f, ratio, 30, 900))
        _summary(r)
        st.metric("Late response amplitude", f"{r.late_response_amplitude_m:.2f} m")


def render():
    _init()
    _reuse()
    st.header("🌀 The Boing Machine")
    st.markdown("Explore ideal oscillation, damping, driving, and resonance.")
    revealed = mission_ui.prediction_quiz(
        key=state_key("quiz"),
        question="If you pull an ideal spring farther, one full boing takes...",
        options=["More time", "Less time", "Almost exactly the same time"],
        correct_index=2,
        reveal_text="The ideal period depends on mass and stiffness, not amplitude.",
        mission_id="spring_predict",
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
    except PhysicsValidationError as error:
        st.error(f"That setup can't run yet: {error}")
