"""Four-mode Big Fall page."""

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
from physics_playground.simulation_cache import cached_tunnel
from physics_playground.state_keys import migrate_simulation_keys, simulation_key
from physics_playground.subjects.mechanics.earth_tunnel.charts import plot_figure
from physics_playground.subjects.mechanics.earth_tunnel.missions import evaluate_tunnel_missions
from physics_playground.subjects.mechanics.earth_tunnel.physics import (
    TunnelModel,
    TunnelParameters,
)
from physics_playground.subjects.mechanics.earth_tunnel.scene import (
    PLAYER_HEIGHT,
    build_tunnel_canvas,
    build_tunnel_comparison_canvas,
)
from physics_playground.units import (
    EARTH_GRAVITY_M_S2,
    EARTH_RADIUS_M,
    MARS_GRAVITY_M_S2,
    MARS_RADIUS_M,
    MOON_GRAVITY_M_S2,
    MOON_RADIUS_M,
)
from physics_playground.validation import PhysicsValidationError

PLANETS = {
    "Earth 🌍": (EARTH_RADIUS_M, EARTH_GRAVITY_M_S2),
    "The Moon 🌕": (MOON_RADIUS_M, MOON_GRAVITY_M_S2),
    "Mars 🔴": (MARS_RADIUS_M, MARS_GRAVITY_M_S2),
}
VERSION = "tunnel-2.0"
ID = "earth_tunnel"


def state_key(name: str) -> str:
    return simulation_key(ID, name)


def _init():
    migrate_simulation_keys(
        st.session_state,
        ID,
        {
            "tunnel_nonce": "nonce",
            "tunnel_launched": "launched",
            "tunnel_compare_nonce": "compare_nonce",
            "tunnel_compare_signature": "compare_signature",
            "tunnel_quiz_guess": "quiz_guess",
            "tunnel_quiz_revealed": "quiz_revealed",
            "tunnel_quiz_lock": "quiz_lock",
            "tunnel_custom_radius": "custom_radius",
            "tunnel_custom_g": "custom_gravity",
            "tunnel_start": "start",
            "tunnel_model": "model",
            "tunnel_planet": "planet",
            "tunnel_learning_mode": "learning_mode",
            "tunnel_observation": "observation",
            "tunnel_compare_observation": "compare_observation",
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
    c[0].metric("Model", r.parameters.model.value)
    c[1].metric("Opposite-point time", f"{r.opposite_time_s / 60:.1f} min")
    c[2].metric("Center speed", f"{r.maximum_speed_m_s / 1000:.2f} km/s")
    st.caption(
        f"Text outcome: the {r.parameters.model.value.lower()} reaches the opposite turning point in {r.opposite_time_s / 60:.1f} minutes and is fastest at the center."
    )


def _metrics(r):
    return {
        "period_s": r.period_s,
        "opposite_time_s": r.opposite_time_s,
        "maximum_speed_m_s": r.maximum_speed_m_s,
        "energy_drift_percent": r.energy_drift_fraction * 100,
    }


def _record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id="earth_tunnel",
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("quiz_guess")),
        result_summary=f"{r.parameters.model.value}: {r.opposite_time_s / 60:.1f} min to opposite point",
        metrics=_metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def _award(r):
    return mission_ui.process_run("earth_tunnel", evaluate_tunnel_missions(r))


def _reuse():
    q = st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id") != "earth_tunnel":
        return
    p = q["parameters"]
    st.session_state[state_key("custom_radius")] = int(
        round(float(p["radius_m"]) / 1000 / 100) * 100
    )
    st.session_state[state_key("custom_gravity")] = float(p["surface_gravity_m_s2"])
    st.session_state[state_key("start")] = (
        "Halfway down" if float(p["start_fraction"]) < 1 else "Surface"
    )
    st.session_state[state_key("model")] = p["model"]
    st.session_state[state_key("planet")] = "Custom planet 🪐"
    st.session_state[state_key("learning_mode")] = "Explore"
    del st.session_state[REUSE_REQUEST_KEY]


def render_explore():
    mode_heading(LearningMode.EXPLORE, "Fall through a planet")
    planet = st.radio(
        "Planet", [*PLANETS, "Custom planet 🪐"], horizontal=True, key=state_key("planet")
    )
    if planet.startswith("Custom"):
        c1, c2 = st.columns(2)
        with c1:
            radius_km = st.slider(
                "Custom radius (km)", 500, 8000, 3000, 100, key=state_key("custom_radius")
            )
        with c2:
            g = st.slider(
                "Custom surface gravity",
                1.0,
                20.0,
                EARTH_GRAVITY_M_S2,
                0.01,
                key=state_key("custom_gravity"),
            )
        radius = radius_km * 1000
    else:
        radius, g = PLANETS[planet]
    start = st.radio(
        "Starting point", ["Surface", "Halfway down"], horizontal=True, key=state_key("start")
    )
    model = TunnelModel(
        st.selectbox(
            "Planet interior model", [m.value for m in TunnelModel], key=state_key("model")
        )
    )
    gradient = 0.75
    if model == TunnelModel.RADIAL:
        gradient = st.slider("Center-to-surface density gradient", 0.0, 0.95, 0.75, 0.05)
    p = TunnelParameters(radius, g, 1 if start == "Surface" else 0.5, model, gradient)
    r = cached_tunnel(p)
    _summary(r)
    autoplay = st.session_state[state_key("launched")] == p.to_dict()
    canvas_embed.show(
        build_tunnel_canvas(
            r, seed=20262300 + st.session_state[state_key("nonce")], autoplay=autoplay
        ),
        height=PLAYER_HEIGHT,
    )
    obs = st.text_input("Optional notebook observation", key=state_key("observation"))
    if st.button("🕳️ JUMP IN!", type="primary", use_container_width=True):
        st.session_state[state_key("nonce")] += 1
        st.session_state[state_key("launched")] = p.to_dict()
        badges = _award(r)
        _record(r, 20262300 + st.session_state[state_key("nonce")], obs, badges=badges)
        st.rerun()
    mission_ui.mission_checklist("The Big Fall")


def _pair(kind):
    if kind == "Surface versus halfway start":
        items = [
            (
                "Surface",
                cached_tunnel(TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2, 1)),
                "#42A5F5",
            ),
            (
                "Halfway",
                cached_tunnel(TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2, 0.5)),
                "#FF8A65",
            ),
        ]
        change = ChangedVariable("Starting amplitude", "Surface", "Halfway")
    elif kind == "Earth versus Moon versus custom planet":
        items = [
            (
                "Earth",
                cached_tunnel(TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2)),
                "#42A5F5",
            ),
            ("Moon", cached_tunnel(TunnelParameters(MOON_RADIUS_M, MOON_GRAVITY_M_S2)), "#B0BEC5"),
            ("Custom", cached_tunnel(TunnelParameters(3000000, 12)), "#AB47BC"),
        ]
        change = ChangedVariable("Planet", "Earth", "Moon and custom")
    else:
        items = [
            (
                "Uniform",
                cached_tunnel(
                    TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2, model=TunnelModel.UNIFORM)
                ),
                "#42A5F5",
            ),
            (
                "Radial",
                cached_tunnel(
                    TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2, model=TunnelModel.RADIAL)
                ),
                "#FF8A65",
            ),
        ]
        change = ChangedVariable("Interior model", "Uniform density", "Radial density")
    return items, change


def render_compare():
    mode_heading(LearningMode.COMPARE, "Overlay falls")
    kind = st.selectbox(
        "Comparison",
        [
            "Surface versus halfway start",
            "Earth versus Moon versus custom planet",
            "Uniform-density versus radial-density model",
        ],
    )
    items, change = _pair(kind)
    changed_variable_banner(change)
    sig = {"kind": kind}
    obs = st.text_input("Optional comparison observation", key=state_key("compare_observation"))
    if st.button("▶ Run comparison", type="primary", use_container_width=True):
        st.session_state[state_key("compare_nonce")] += 1
        st.session_state[state_key("compare_signature")] = sig
        n = st.session_state[state_key("compare_nonce")]
        for i, (label, r, _) in enumerate(items):
            _record(r, 20262400 + n + i, obs, f"Run {chr(65 + i)} — {label}")
    canvas_embed.show(
        build_tunnel_comparison_canvas(
            items,
            seed=20262500 + st.session_state[state_key("compare_nonce")],
            autoplay=st.session_state[state_key("compare_signature")] == sig,
        ),
        height=PLAYER_HEIGHT,
    )
    if len(items) >= 2:
        comparison_metrics(
            {k: (k, v) for k, v in _metrics(items[0][1]).items()},
            {k: (k, v) for k, v in _metrics(items[1][1]).items()},
        )


def _latest():
    if not st.session_state[state_key("launched")]:
        return TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2)
    d = dict(st.session_state[state_key("launched")])
    d["model"] = TunnelModel(d["model"])
    return TunnelParameters(**d)


def render_analyze():
    mode_heading(LearningMode.ANALYZE, "Position, velocity, acceleration, and energy")
    r = cached_tunnel(_latest())
    _summary(r)
    for plot in r.plots:
        fig = plot_figure(plot)
        render_chart(fig, f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.")
        plt.close(fig)


def render_model():
    mode_heading(LearningMode.MODEL, "Why uniform density becomes SHM")
    st.latex(r"M(r)=M\left(\frac rR\right)^3")
    st.latex(r"a(r)=-\frac{GM(r)}{r^2}=-\frac{GM}{R^3}r=-\frac gRr")
    st.latex(r"\ddot r+\frac gRr=0,\quad T=2\pi\sqrt{R/g}")
    st.markdown(
        "Uniform density makes enclosed mass grow as r³, so gravitational acceleration becomes proportional to −r: exactly the defining equation of simple harmonic motion. The radial-density model instead integrates the enclosed mass of a center-heavy profile with RK4."
    )
    assumptions = cached_tunnel(TunnelParameters(EARTH_RADIUS_M, EARTH_GRAVITY_M_S2)).assumptions
    assumptions_panel(
        assumptions,
        (
            "Pressure, heat, and the physical feasibility of the tunnel are ignored.",
            "The real Earth is layered and not perfectly radial.",
            "Rotation and the Coriolis effect are omitted.",
            "The radial profile is illustrative, not a seismological Earth model.",
        ),
    )


def render():
    _init()
    _reuse()
    st.header("🕳️ The Big Fall")
    st.markdown(
        "Default model: **uniform-density planet**. An advanced radial-density profile is also available."
    )
    revealed = mission_ui.prediction_quiz(
        key=state_key("quiz"),
        question="About how long does the ideal uniform-density Earth fall take from one surface to the other?",
        options=["5 minutes", "42 minutes", "3 hours", "Forever"],
        correct_index=1,
        reveal_text="It takes about **42 minutes** to reach the opposite surface.",
        mission_id="tunnel_predict",
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
