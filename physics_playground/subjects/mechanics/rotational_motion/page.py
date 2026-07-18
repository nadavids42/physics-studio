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
from .physics import BodyShape, RotationalParameters, simulate

ID = "rotational_motion"
VERSION = "rotational-motion-1.0"


def numbers(r):
    return {
        "moment_of_inertia_kg_m2": r.moment_of_inertia_kg_m2,
        "angular_acceleration_rad_s2": r.angular_acceleration_rad_s2,
        "final_angular_velocity_rad_s": r.angular_velocity_rad_s[-1],
        "final_angle_rad": r.angular_position_rad[-1],
        "final_rotational_energy_j": r.rotational_kinetic_energy_j[-1],
    }


def animation(r, seed):
    p = r.parameters
    show(
        document(
            "rotation",
            [{"id": "body", "label": "Body", "x": [0, r.angular_position_rad[-1]]}],
            message=r.outcome,
            seed=seed,
            autoplay=False,
            scene_config={
                "shape": BodyShape(p.shape).value,
                "torqueNm": p.torque_n_m,
                "omegaRadS": r.angular_velocity_rad_s[-1],
                "angularAccelerationRadS2": r.angular_acceleration_rad_s2,
            },
        )
    )


def controls(key="rotation"):
    c1, c2 = st.columns(2)
    with c1:
        shape = BodyShape(
            st.selectbox("Body shape", [x.value for x in BodyShape], index=2, key=f"{key}_shape")
        )
        mass = st.slider("Mass (kg)", 0.2, 30.0, 5.0, 0.2, key=f"{key}_mass")
        size = st.slider("Radius or rod length (m)", 0.1, 5.0, 1.0, 0.1, key=f"{key}_size")
    with c2:
        torque = st.slider("Applied torque (N·m)", -50.0, 50.0, 10.0, 1.0, key=f"{key}_torque")
        omega = st.slider(
            "Initial angular velocity (rad/s)", -20.0, 20.0, 0.0, 0.5, key=f"{key}_omega"
        )
        duration = st.slider("Duration (s)", 0.5, 10.0, 5.0, 0.5, key=f"{key}_duration")
    return RotationalParameters(mass, size, shape, torque, omega, duration)


def explore():
    mode_heading(LearningMode.EXPLORE, "Apply a torque")
    r = simulate(controls())
    metric_table(
        {
            "Moment of inertia": f"{r.moment_of_inertia_kg_m2:.2f} kg·m²",
            "Angular acceleration": f"{r.angular_acceleration_rad_s2:.2f} rad/s²",
            "Final speed": f"{r.angular_velocity_rad_s[-1]:.2f} rad/s",
        }
    )
    st.caption("Text outcome: " + r.outcome)
    animation(r, 20262401)
    obs = st.text_input("Optional notebook observation", key="rotation_obs")
    if st.button("🌀 Spin body", type="primary", use_container_width=True):
        record(
            ID,
            r.parameters.to_dict(),
            st.session_state.get("rotation_quiz_guess"),
            r.outcome,
            numbers(r),
            mission_ui.process_run(ID, evaluate(r)),
            20262401,
            VERSION,
            obs,
        )
        st.rerun()
    mission_ui.mission_checklist("Rotational Motion")


def compare():
    mode_heading(LearningMode.COMPARE, "Disk versus hoop")
    a = simulate(RotationalParameters(shape=BodyShape.SOLID_DISK))
    b = simulate(RotationalParameters(shape=BodyShape.HOOP))
    changed_variable_banner(ChangedVariable("Inertia model", "Solid disk", "Hoop"))
    metric_table(
        {
            "Disk acceleration": f"{a.angular_acceleration_rad_s2:.2f} rad/s²",
            "Hoop acceleration": f"{b.angular_acceleration_rad_s2:.2f} rad/s²",
        }
    )
    if st.button("▶ Run shape comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262411), ("Run B", b, 20262412)):
            record(
                ID,
                r.parameters.to_dict(),
                "The disk accelerates faster",
                r.outcome,
                numbers(r),
                mission_ui.process_run(ID, evaluate(r, True)),
                seed,
                VERSION,
                None,
                label,
            )
    animation(b, 20262412)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Angular kinematics and energy")
    r = simulate(controls("rotation_analysis"))
    time = list(r.time_s)
    angle = series_figure(
        x=time,
        series={"Angular position": list(r.angular_position_rad)},
        x_label="Time (s)",
        y_label="Angle (rad)",
        title="Angular position",
    )
    render_chart(angle, "Constant torque produces quadratically changing angular position.")
    plt.close(angle)
    speed = series_figure(
        x=time,
        series={"Angular velocity": list(r.angular_velocity_rad_s)},
        x_label="Time (s)",
        y_label="Angular velocity (rad/s)",
        title="Angular velocity",
    )
    render_chart(speed, "Constant torque produces linearly changing angular velocity.")
    plt.close(speed)
    energy = series_figure(
        x=time,
        series={
            "Rotational energy": list(r.rotational_kinetic_energy_j),
            "Work done": list(r.work_done_j),
        },
        x_label="Time (s)",
        y_label="Energy (J)",
        title="Rotational work and energy",
    )
    render_chart(
        energy,
        "Applied work equals the change in rotational kinetic energy relative to its initial value.",
    )
    plt.close(energy)


def model():
    mode_heading(LearningMode.MODEL, "Torque, inertia, and angular motion")
    st.latex(r"\tau=I\alpha\quad \omega=\omega_0+\alpha t\quad \theta=\omega_0t+\frac12\alpha t^2")
    st.latex(r"K_{rot}=\frac12I\omega^2")
    st.markdown(
        "Supported inertia models: point mass/hoop $MR^2$, disk $MR^2/2$, sphere $2MR^2/5$, and center-pivoted rod $ML^2/12$."
    )
    assumptions_panel(
        (
            ModelAssumption("rigid", "Body is perfectly rigid"),
            ModelAssumption("constant", "Applied torque is constant"),
        ),
        ("No bearing friction.", "No deformation.", "Rotation is about one fixed principal axis."),
    )


def render():
    st.header("🌀 Rotational Motion")
    revealed = mission_ui.prediction_quiz(
        key="rotation_quiz",
        question="The same torque acts on a disk and hoop with equal mass and radius. Which accelerates faster?",
        options=["Solid disk", "Hoop", "They match"],
        correct_index=0,
        reveal_text="The disk has half the hoop's moment of inertia, so its angular acceleration is larger.",
        mission_id="rotation_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key="rotation_mode")
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
