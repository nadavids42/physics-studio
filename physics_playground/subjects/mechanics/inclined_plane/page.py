import math

import matplotlib.pyplot as plt
import streamlit as st

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
from physics_playground.subjects.mechanics.canvas import document
from physics_playground.subjects.mechanics.ui import metric_table, record, show

from .missions import evaluate
from .physics import InclinedPlaneParameters, simulate

ID = "inclined_plane"
VERSION = "inclined-plane-1.0"


def params(prefix="incline"):
    c1, c2 = st.columns(2)
    with c1:
        m = st.slider("Block mass (kg)", 0.2, 20.0, 2.0, 0.2, key=f"{prefix}_mass")
        a = st.slider("Ramp angle (degrees)", 0, 75, 30, key=f"{prefix}_angle")
    with c2:
        mus = st.slider("Static friction coefficient", 0.0, 1.5, 0.3, 0.05, key=f"{prefix}_mus")
        ratio = st.slider(
            "Kinetic friction as a fraction of static friction",
            0.0,
            1.0,
            0.67,
            0.01,
            key=f"{prefix}_muk_ratio",
        )
        muk = mus * ratio
    return InclinedPlaneParameters(m, a, mus, muk)


def metrics(r):
    return {
        "Acceleration": f"{r.acceleration_m_s2:.2f} m/s²",
        "Normal force": f"{r.normal_force_n:.2f} N",
        "Final speed": f"{r.final_speed_m_s:.2f} m/s",
    }


def numeric(r):
    return {
        "acceleration_m_s2": r.acceleration_m_s2,
        "normal_force_n": r.normal_force_n,
        "friction_force_n": r.friction_force_n,
        "final_speed_m_s": r.final_speed_m_s,
        "critical_angle_deg": r.critical_angle_deg,
    }


def animate(r, seed, autoplay=True):
    p = r.parameters
    end = 1 if r.moving else 0
    largest = max(r.normal_force_n, r.down_slope_force_n, r.friction_force_n, abs(r.net_force_n), 1)

    def length(value):
        return 28 + 40 * abs(value) / largest

    theta = math.radians(p.angle_deg)
    down = (math.cos(theta), -math.sin(theta))
    normal = (-math.sin(theta), math.cos(theta))
    vectors = [
        {
            "dx": 0,
            "dy": -1,
            "role": "gravity",
            "label": f"weight {p.mass_kg * p.gravity_m_s2:.1f} N",
            "scale_mode": "normalized",
            "fixed_length_px": length(p.mass_kg * p.gravity_m_s2),
        },
        {
            "dx": normal[0],
            "dy": normal[1],
            "role": "normal_force",
            "label": f"normal {r.normal_force_n:.1f} N",
            "scale_mode": "normalized",
            "fixed_length_px": length(r.normal_force_n),
        },
    ]
    if r.friction_force_n:
        vectors.append(
            {
                "dx": -down[0],
                "dy": -down[1],
                "role": "friction",
                "label": f"friction {r.friction_force_n:.1f} N",
                "scale_mode": "normalized",
                "fixed_length_px": length(r.friction_force_n),
            }
        )
    if abs(r.net_force_n) > 1e-9:
        vectors.append(
            {
                "dx": down[0],
                "dy": down[1],
                "role": "net_force",
                "label": f"net {r.net_force_n:.1f} N",
                "scale_mode": "normalized",
                "fixed_length_px": length(r.net_force_n),
            }
        )
    show(
        document(
            "ramp",
            [{"id": "block", "label": "Block", "x": [0, end]}],
            message=r.outcome,
            seed=seed,
            autoplay=autoplay,
            scene_config={
                "angleDeg": p.angle_deg,
                "criticalAngleDeg": r.critical_angle_deg,
                "moving": r.moving,
                "motionState": "sliding" if r.moving else "static equilibrium",
                "vectors": vectors,
            },
        )
    )


def explore():
    mode_heading(LearningMode.EXPLORE, "Will it slide?")
    r = simulate(params())
    metric_table(metrics(r))
    st.caption("Text outcome: " + r.outcome)
    animate(r, 20262001, False)
    obs = st.text_input("Optional notebook observation", key="incline_obs")
    if st.button("▶ Run ramp", type="primary", use_container_width=True):
        badges = mission_ui.process_run(ID, evaluate(r))
        record(
            ID,
            r.parameters.to_dict(),
            st.session_state.get("incline_quiz_guess"),
            r.outcome,
            numeric(r),
            badges,
            20262001,
            VERSION,
            obs,
        )
        st.rerun()
    mission_ui.mission_checklist("Inclined Plane")


def compare():
    mode_heading(LearningMode.COMPARE, "Smooth versus rough")
    angle = st.slider("Comparison ramp angle", 5, 70, 35)
    a = simulate(
        InclinedPlaneParameters(angle_deg=angle, static_friction=0.1, kinetic_friction=0.05)
    )
    b = simulate(
        InclinedPlaneParameters(angle_deg=angle, static_friction=0.7, kinetic_friction=0.5)
    )
    changed_variable_banner(ChangedVariable("Friction", "Low", "High"))
    metric_table(
        {
            "Run A acceleration": f"{a.acceleration_m_s2:.2f} m/s²",
            "Run B acceleration": f"{b.acceleration_m_s2:.2f} m/s²",
        }
    )
    if st.button("▶ Run comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262011), ("Run B", b, 20262012)):
            record(
                ID,
                r.parameters.to_dict(),
                "Lower friction slides faster",
                r.outcome,
                numeric(r),
                mission_ui.process_run(ID, evaluate(r)),
                seed,
                VERSION,
                None,
                label,
            )
    animate(b, 20262012, False)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Forces and slipping threshold")
    mu = st.slider("Static friction for scan", 0.0, 1.2, 0.3, 0.05)
    angles = list(range(0, 76, 5))
    values = [
        simulate(
            InclinedPlaneParameters(angle_deg=a, static_friction=mu, kinetic_friction=min(0.2, mu))
        ).acceleration_m_s2
        for a in angles
    ]
    figure = series_figure(
        x=angles,
        series={"Acceleration": values},
        x_label="Ramp angle (degrees)",
        y_label="Acceleration (m/s²)",
        title="Acceleration versus ramp angle",
    )
    render_chart(
        figure,
        "Acceleration remains zero below the slipping threshold, then rises with ramp angle.",
    )
    plt.close(figure)


def model():
    mode_heading(LearningMode.MODEL, "Resolve gravity along the ramp")
    st.latex(r"N=mg\cos\theta\quad F_\parallel=mg\sin\theta")
    st.latex(r"F_{s,max}=\mu_sN\quad a=g(\sin\theta-\mu_k\cos\theta)")
    assumptions_panel(
        (
            ModelAssumption("point", "Rigid block and ramp"),
            ModelAssumption("constant", "Constant friction coefficients"),
        ),
        (
            "No air resistance.",
            "The ramp does not deform.",
            "Friction changes instantly from static to kinetic.",
        ),
    )


def render():
    st.header("📐 Inclined Plane with Friction")
    revealed = mission_ui.prediction_quiz(
        key="incline_quiz",
        question="If a ramp gets steeper while friction stays the same, is the block more likely to slide?",
        options=["Yes", "No", "Mass alone decides"],
        correct_index=0,
        reveal_text="The downhill part of gravity grows relative to the normal force.",
        mission_id="incline_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key="incline_mode")
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
