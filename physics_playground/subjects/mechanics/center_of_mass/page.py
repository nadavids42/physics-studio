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
from .physics import CenterOfMassParameters, simulate

ID = "center_of_mass"
VERSION = "center-of-mass-1.0"


def values(r):
    return {
        "center_of_mass_m": r.center_of_mass_m,
        "total_mass_kg": r.total_mass_kg,
        "left_mass_kg": r.left_mass_kg,
        "right_mass_kg": r.right_mass_kg,
    }


def animation(r, seed):
    p = r.parameters
    objects = [
        {
            "label": "Mass 1",
            "mass": p.mass_1_kg,
            "position": p.position_1_m,
            "role": "accent",
            "selected": p.mass_1_kg >= p.mass_2_kg,
        },
        {
            "label": "Mass 2",
            "mass": p.mass_2_kg,
            "position": p.position_2_m,
            "role": "energy",
            "selected": p.mass_2_kg > p.mass_1_kg,
        },
    ]
    if p.mass_3_kg > 0:
        objects.append(
            {
                "label": "Mass 3",
                "mass": p.mass_3_kg,
                "position": p.position_3_m,
                "role": "displacement",
                "selected": False,
            }
        )
    show(
        document(
            "center of mass",
            [],
            message=r.outcome,
            seed=seed,
            autoplay=False,
            scene_config={"objects": objects, "centerM": r.center_of_mass_m},
        )
    )


def explore():
    mode_heading(LearningMode.EXPLORE, "Find the balance point")
    c1, c2, c3 = st.columns(3)
    with c1:
        m1 = st.slider("Mass 1 (kg)", 0.0, 10.0, 2.0, 0.5)
        x1 = st.slider("Position 1 (m)", -5.0, 5.0, -2.0, 0.5)
    with c2:
        m2 = st.slider("Mass 2 (kg)", 0.0, 10.0, 3.0, 0.5)
        x2 = st.slider("Position 2 (m)", -5.0, 5.0, 2.0, 0.5)
    with c3:
        m3 = st.slider("Optional mass 3 (kg)", 0.0, 10.0, 0.0, 0.5)
        x3 = st.slider("Position 3 (m)", -5.0, 5.0, 0.0, 0.5)
    r = simulate(CenterOfMassParameters(m1, x1, m2, x2, m3, x3))
    metric_table(
        {"Center of mass": f"{r.center_of_mass_m:.2f} m", "Total mass": f"{r.total_mass_kg:.1f} kg"}
    )
    st.caption("Text outcome: " + r.outcome)
    animation(r, 20262201)
    obs = st.text_input("Optional notebook observation", key="com_obs")
    if st.button("▶ Find balance point", type="primary", use_container_width=True):
        record(
            ID,
            r.parameters.to_dict(),
            st.session_state.get("com_quiz_guess"),
            r.outcome,
            values(r),
            mission_ui.process_run(ID, evaluate(r)),
            20262201,
            VERSION,
            obs,
        )
        st.rerun()
    mission_ui.mission_checklist("Center of Mass")


def compare():
    mode_heading(LearningMode.COMPARE, "Equal versus unequal masses")
    a = simulate(CenterOfMassParameters(2, -2, 2, 2))
    b = simulate(CenterOfMassParameters(2, -2, 6, 2))
    changed_variable_banner(ChangedVariable("Mass 2", "2 kg", "6 kg"))
    metric_table(
        {
            "Run A center": f"{a.center_of_mass_m:.2f} m",
            "Run B center": f"{b.center_of_mass_m:.2f} m",
        }
    )
    if st.button("▶ Run mass comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262211), ("Run B", b, 20262212)):
            record(
                ID,
                r.parameters.to_dict(),
                "The center shifts toward the heavier mass",
                r.outcome,
                values(r),
                mission_ui.process_run(ID, evaluate(r)),
                seed,
                VERSION,
                None,
                label,
            )
    animation(b, 20262212)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Move one mass")
    positions = [x / 2 for x in range(-10, 11)]
    centers = [simulate(CenterOfMassParameters(2, -2, 3, x)).center_of_mass_m for x in positions]
    figure = series_figure(
        x=positions,
        series={"Center of mass": centers},
        x_label="Mass 2 position (m)",
        y_label="Center position (m)",
        title="Center position as mass 2 moves",
    )
    render_chart(
        figure,
        "Moving the second mass right shifts the center of mass right in a straight-line relationship.",
    )
    plt.close(figure)


def model():
    mode_heading(LearningMode.MODEL, "A mass-weighted average")
    st.latex(r"x_{cm}=\frac{\sum_i m_ix_i}{\sum_i m_i}")
    assumptions_panel(
        (
            ModelAssumption("particles", "Objects are represented by point masses"),
            ModelAssumption("frame", "All positions use one inertial coordinate system"),
        ),
        (
            "Object shape and internal mass distribution are omitted.",
            "The visualization is one-dimensional.",
            "Masses do not interact dynamically.",
        ),
    )


def render():
    st.header("🎯 Center of Mass")
    revealed = mission_ui.prediction_quiz(
        key="com_quiz",
        question="If the mass on the right becomes heavier, where does the balance point move?",
        options=["Left", "Right", "It stays fixed"],
        correct_index=1,
        reveal_text="The center of mass shifts toward the heavier object.",
        mission_id="com_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key="com_mode")
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
