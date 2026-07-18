import matplotlib.pyplot as plt
import streamlit as st

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
from physics_playground.subjects.mechanics.canvas import document
from physics_playground.subjects.mechanics.ui import metric_table, record, show

from .missions import evaluate
from .physics import LeverParameters, simulate

ID = "torque_levers"
VERSION = "lever-1.0"


def values(r):
    return {
        "load_torque_n_m": r.load_torque_n_m,
        "effort_torque_n_m": r.effort_torque_n_m,
        "net_torque_n_m": r.net_torque_n_m,
        "required_balance_force_n": r.required_balance_force_n,
        "mechanical_advantage": r.mechanical_advantage,
    }


def animation(r, seed):
    p = r.parameters
    show(
        document(
            "lever",
            [{"id": "beam", "label": "Lever", "x": [0, max(-12, min(12, r.net_torque_n_m / 10))]}],
            message=r.outcome,
            seed=seed,
            autoplay=False,
            scene_config={
                "loadArmM": p.load_arm_m,
                "effortArmM": p.effort_arm_m,
                "loadForceN": p.load_force_n,
                "effortForceN": p.effort_force_n,
                "loadTorqueNm": r.load_torque_n_m,
                "effortTorqueNm": r.effort_torque_n_m,
                "netTorqueNm": r.net_torque_n_m,
            },
        )
    )


def explore():
    mode_heading(LearningMode.EXPLORE, "Balance the beam")
    c1, c2 = st.columns(2)
    with c1:
        load = st.slider("Load force (N)", 0.0, 500.0, 200.0, 10.0)
        la = st.slider("Load arm (m)", 0.1, 3.0, 0.5, 0.1)
    with c2:
        effort = st.slider("Effort force (N)", 0.0, 500.0, 80.0, 10.0)
        ea = st.slider("Effort arm (m)", 0.1, 3.0, 1.5, 0.1)
    r = simulate(LeverParameters(load, la, effort, ea))
    metric_table(
        {
            "Load torque": f"{r.load_torque_n_m:.1f} N·m",
            "Effort torque": f"{r.effort_torque_n_m:.1f} N·m",
            "Advantage": f"{r.mechanical_advantage:.2f}×",
        }
    )
    st.caption("Text outcome: " + r.outcome)
    animation(r, 20262101)
    obs = st.text_input("Optional notebook observation", key="lever_obs")
    if st.button("▶ Test lever", type="primary", use_container_width=True):
        record(
            ID,
            r.parameters.to_dict(),
            st.session_state.get("lever_quiz_guess"),
            r.outcome,
            values(r),
            kidtools.process_run(ID, evaluate(r)),
            20262101,
            VERSION,
            obs,
        )
        st.rerun()
    kidtools.mission_checklist("Torque and Levers")


def compare():
    mode_heading(LearningMode.COMPARE, "Short versus long effort arm")
    a = simulate(LeverParameters(effort_arm_m=0.5))
    b = simulate(LeverParameters(effort_arm_m=2.5))
    changed_variable_banner(ChangedVariable("Effort arm", "0.5 m", "2.5 m"))
    metric_table(
        {
            "Run A torque": f"{a.effort_torque_n_m:.1f} N·m",
            "Run B torque": f"{b.effort_torque_n_m:.1f} N·m",
        }
    )
    if st.button("▶ Run lever comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262111), ("Run B", b, 20262112)):
            record(
                ID,
                r.parameters.to_dict(),
                "Longer arm creates more torque",
                r.outcome,
                values(r),
                kidtools.process_run(ID, evaluate(r)),
                seed,
                VERSION,
                None,
                label,
            )
    animation(b, 20262112)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Torque versus lever arm")
    arms = [x / 10 for x in range(1, 31)]
    figure = series_figure(
        x=arms,
        series={"Torque at 80 N": [80 * x for x in arms]},
        x_label="Lever arm (m)",
        y_label="Torque (N·m)",
        title="Torque versus lever arm",
    )
    render_chart(figure, "At fixed force, torque increases linearly with distance from the pivot.")
    plt.close(figure)


def model():
    mode_heading(LearningMode.MODEL, "Moments about a pivot")
    st.latex(r"\tau=rF_\perp\qquad \sum\tau=0\text{ at balance}")
    assumptions_panel(
        (
            ModelAssumption("rigid", "The beam is rigid and massless"),
            ModelAssumption("perpendicular", "Forces act perpendicular to the beam"),
        ),
        (
            "Pivot friction is omitted.",
            "The beam's own weight is omitted.",
            "Dynamic angular acceleration is illustrative only.",
        ),
    )


def render():
    st.header("⚖️ Torque and Levers")
    revealed = kidtools.prediction_quiz(
        key="lever_quiz",
        question="With the same force, where should you push to create more turning effect?",
        options=["Near the pivot", "Far from the pivot", "Distance does not matter"],
        correct_index=1,
        reveal_text="Torque equals force times perpendicular distance from the pivot.",
        mission_id="lever_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key="lever_mode")
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
