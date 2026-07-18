"""Four-mode Planet Launcher page."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import embed as canvas_embed
from physics_playground.canvas.orbit import (
    PLAYER_HEIGHT,
    build_orbit_canvas,
    build_orbit_comparison_canvas,
)
from physics_playground.missions import ui as mission_ui
from physics_playground.missions.orbit import evaluate_orbit_missions
from physics_playground.models.orbit import (
    OrbitParameters,
    timestep_warning,
)
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
from physics_playground.presentation.orbit_charts import plot_figure
from physics_playground.simulation_cache import cached_orbit
from physics_playground.validation import PhysicsValidationError

VERSION = "orbit-verlet-1.0"


def _init():
    for k, v in (
        ("orbit_nonce", 0),
        ("orbit_launched", None),
        ("orbit_compare_nonce", 0),
        ("orbit_compare_signature", None),
    ):
        st.session_state.setdefault(k, v)


def _summary(r):
    c = st.columns(4)
    c[0].metric("Outcome", r.outcome.value)
    c[1].metric("Eccentricity", f"{r.eccentricity:.3f}")
    c[2].metric("Periapsis", f"{r.periapsis:.2f}" if r.periapsis else "n/a")
    c[3].metric("Apoapsis", f"{r.apoapsis:.2f}" if r.apoapsis else "n/a")
    st.caption(
        f"Text outcome: {r.outcome.value}; eccentricity {r.eccentricity:.3f}, periapsis {r.periapsis if r.periapsis is not None else 'not applicable'}, apoapsis {r.apoapsis if r.apoapsis is not None else 'not applicable'}."
    )


def _metrics(r):
    return {
        "eccentricity": r.eccentricity,
        "periapsis": r.periapsis or 0,
        "apoapsis": r.apoapsis or 0,
        "energy_drift_percent": r.energy_drift_fraction * 100,
        "angular_momentum_drift_percent": r.angular_momentum_drift_fraction * 100,
    }


def _record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id="orbital_gravity",
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get("orbit_quiz_guess"),
        result_summary=f"{r.outcome.value}; eccentricity {r.eccentricity:.3f}",
        metrics=_metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def _award(r):
    return mission_ui.process_run("orbital_gravity", evaluate_orbit_missions(r))


def _reuse():
    q = st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id") != "orbital_gravity":
        return
    p = q["parameters"]
    st.session_state["orbit_mu"] = float(p["gravitational_parameter"])
    st.session_state["orbit_radius"] = float(p["launch_radius"])
    st.session_state["orbit_speed"] = float(p["tangential_speed"])
    st.session_state["orbit_dt"] = float(p["time_step"])
    st.session_state["orbit_learning_mode"] = "Explore"
    del st.session_state[REUSE_REQUEST_KEY]


def render_explore():
    mode_heading(LearningMode.EXPLORE, "Choose a launch speed")
    c1, c2 = st.columns(2)
    with c1:
        mu = st.slider("Central gravity μ", 1.0, 80.0, 20.0, 0.5, key="orbit_mu")
        radius = st.slider("Launch radius", 1.0, 30.0, 7.0, 0.1, key="orbit_radius")
    circular = (mu / radius) ** 0.5
    escape = (2 * mu / radius) ** 0.5
    with c2:
        speed = st.slider(
            "Tangential launch speed", 0.0, escape * 1.4, circular, 0.02, key="orbit_speed"
        )
        dt = st.number_input("Time step", 0.001, 0.2, 0.02, 0.005, key="orbit_dt")
    st.caption(f"Circular-speed marker: **{circular:.3f}** · Escape-speed marker: **{escape:.3f}**")
    p = OrbitParameters(
        mu, radius, speed, dt, 5000, collision_radius=0.35, escape_radius=max(80, radius * 8)
    )
    warning = timestep_warning(p)
    if warning:
        st.warning(warning)
    r = cached_orbit(p)
    _summary(r)
    autoplay = st.session_state.orbit_launched == p.to_dict()
    canvas_embed.show(
        build_orbit_canvas(r, seed=20261900 + st.session_state.orbit_nonce, autoplay=autoplay),
        height=PLAYER_HEIGHT,
    )
    obs = st.text_input("Optional notebook observation", key="orbit_observation")
    if st.button("🚀 LAUNCH!", type="primary", use_container_width=True):
        st.session_state.orbit_nonce += 1
        st.session_state.orbit_launched = p.to_dict()
        badges = _award(r)
        _record(r, 20261900 + st.session_state.orbit_nonce, obs, badges=badges)
        st.rerun()
    mission_ui.mission_checklist("Planet Launcher")


def _pair(kind):
    if kind == "Circular versus elliptical orbit":
        a = OrbitParameters(20, 7, (20 / 7) ** 0.5)
        b = OrbitParameters(20, 7, (20 / 7) ** 0.5 * 0.72)
        change = ChangedVariable("Launch speed", "Circular", "72% circular")
        labels = ("Circular", "Elliptical")
    elif kind == "Circular versus escape trajectory":
        a = OrbitParameters(20, 7, (20 / 7) ** 0.5)
        b = OrbitParameters(20, 7, (40 / 7) ** 0.5 * 1.03, escape_radius=50)
        change = ChangedVariable("Launch speed", "Circular", "Above escape")
        labels = ("Circular", "Escape")
    elif kind == "Different central masses":
        a = OrbitParameters(10, 7, (10 / 7) ** 0.5)
        b = OrbitParameters(40, 7, (10 / 7) ** 0.5)
        change = ChangedVariable("Central mass μ", "10", "40")
        labels = ("Light center", "Heavy center")
    else:
        a = OrbitParameters(20, 5, (20 / 5) ** 0.5)
        b = OrbitParameters(20, 12, (20 / 5) ** 0.5)
        change = ChangedVariable("Launch radius", "5", "12")
        labels = ("Near", "Far")
    return cached_orbit(a), cached_orbit(b), labels, change


def render_compare():
    mode_heading(LearningMode.COMPARE, "Overlay orbital trajectories")
    kind = st.selectbox(
        "Comparison",
        [
            "Circular versus elliptical orbit",
            "Circular versus escape trajectory",
            "Different central masses",
            "Different launch radii",
        ],
    )
    a, b, labels, change = _pair(kind)
    changed_variable_banner(change)
    sig = {"kind": kind}
    obs = st.text_input("Optional comparison observation", key="orbit_compare_observation")
    if st.button("▶ Run comparison", type="primary", use_container_width=True):
        st.session_state.orbit_compare_nonce += 1
        st.session_state.orbit_compare_signature = sig
        n = st.session_state.orbit_compare_nonce
        _record(a, 20262000 + n, obs, "Run A")
        _record(b, 20262100 + n, obs, "Run B")
    canvas_embed.show(
        build_orbit_comparison_canvas(
            a,
            b,
            labels=labels,
            seed=20262200 + st.session_state.orbit_compare_nonce,
            autoplay=st.session_state.orbit_compare_signature == sig,
        ),
        height=PLAYER_HEIGHT,
    )
    comparison_metrics(
        {k: (k, v) for k, v in _metrics(a).items()}, {k: (k, v) for k, v in _metrics(b).items()}
    )


def _latest():
    return (
        OrbitParameters(**st.session_state.orbit_launched)
        if st.session_state.orbit_launched
        else OrbitParameters(20, 7, (20 / 7) ** 0.5)
    )


def render_analyze():
    mode_heading(LearningMode.ANALYZE, "Conservation and orbital elements")
    r = cached_orbit(_latest())
    _summary(r)
    c = st.columns(2)
    c[0].metric("Numerical energy drift", f"{r.energy_drift_fraction * 100:.5f}%")
    c[1].metric("Angular-momentum drift", f"{r.angular_momentum_drift_fraction * 100:.5f}%")
    for plot in r.plots:
        fig = plot_figure(plot)
        render_chart(fig, f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.")
        plt.close(fig)


def render_model():
    mode_heading(LearningMode.MODEL, "Two-body gravity and velocity Verlet")
    st.latex(r"\vec a=-\mu\frac{\vec r}{|\vec r|^3}")
    st.latex(r"v_c=\sqrt{\mu/r},\quad v_{esc}=\sqrt{2\mu/r}")
    st.latex(r"\epsilon=\frac{v^2}{2}-\frac{\mu}{r},\quad h=|\vec r\times\vec v|")
    st.markdown(
        "Position advances using the current acceleration; velocity then advances using the average of the old and new accelerations. This velocity-Verlet method is time-reversible and strongly improves long-term conservation over the previous Euler step."
    )
    assumptions = cached_orbit(OrbitParameters(20, 7, (20 / 7) ** 0.5)).assumptions
    assumptions_panel(
        assumptions,
        (
            "The central body never moves.",
            "Planet-planet gravity is omitted.",
            "Relativity, drag, and non-spherical gravity are ignored.",
            "Crash and escape boundaries are simplified numerical events.",
        ),
    )


def render():
    _init()
    _reuse()
    st.header("🪐 Planet Launcher")
    st.markdown(
        "Launch a planet and discover circular, elliptical, crash, and escape trajectories."
    )
    revealed = mission_ui.prediction_quiz(
        key="orbit_quiz",
        question="What happens when a planet is thrown much too slowly?",
        options=["It escapes", "It crashes inward", "It makes a circular orbit"],
        correct_index=1,
        reveal_text="Without enough sideways speed, gravity pulls it into the central body.",
        mission_id="orbit_predict",
    )
    if not revealed:
        st.caption("🔬 Make your prediction before speed markers and results are shown.")
        return
    mode = mode_navigation(key="orbit_learning_mode")
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
