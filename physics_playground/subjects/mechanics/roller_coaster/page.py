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
from physics_playground.state_keys import simulation_key
from physics_playground.subjects.mechanics.canvas import document
from physics_playground.subjects.mechanics.ui import metric_table, record, show

from .missions import evaluate
from .physics import RollerCoasterParameters, simulate

ID = "roller_coaster"


def state_key(name: str) -> str:
    canonical = simulation_key(ID, name)
    if name in st.session_state and canonical not in st.session_state:
        st.session_state[canonical] = st.session_state.pop(name)
    return canonical


VERSION = "roller-coaster-1.0"


def numbers(r):
    return {
        "maximum_speed_m_s": r.maximum_speed_m_s,
        "energy_lost_j": r.energy_lost_j,
        "final_mechanical_energy_j": r.mechanical_energy_j[-1] if r.mechanical_energy_j else 0.0,
        "stopping_distance_m": r.stopping_distance_m or r.parameters.track_length_m,
    }


def animation(r, seed):
    p = r.parameters
    normalized = [distance / p.track_length_m for distance in r.distance_m]
    show(
        document(
            "coaster",
            [
                {
                    "id": "car",
                    "label": "Coaster",
                    "x": normalized or [0],
                    "y": list(r.speed_m_s) or [0],
                }
            ],
            message=r.outcome,
            seed=seed,
            autoplay=False,
            scene_config={
                "trackLengthM": p.track_length_m,
                "trackPoints": [
                    {"distance": 0, "height": p.initial_height_m},
                    {"distance": p.track_length_m / 2, "height": p.hill_height_m},
                    {"distance": p.track_length_m, "height": p.final_height_m},
                ],
                "reachableDistanceM": r.distance_m[-1] if r.distance_m else 0,
                "massKg": p.mass_kg,
                "gravityMps2": p.gravity_m_s2,
                "lossPerMeterJ": p.loss_per_meter_j,
            },
        )
    )


def controls(key="coaster"):
    c1, c2 = st.columns(2)
    with c1:
        start = st.slider(
            "Starting height (m)", 1.0, 50.0, 20.0, 1.0, key=state_key(f"{key}_start")
        )
        hill = st.slider(
            "Middle hill height (m)", 0.0, 60.0, 12.0, 1.0, key=state_key(f"{key}_hill")
        )
        finish = st.slider("Final height (m)", 0.0, 40.0, 2.0, 1.0, key=state_key(f"{key}_finish"))
    with c2:
        speed = st.slider(
            "Starting speed (m/s)", 0.0, 25.0, 0.0, 0.5, key=state_key(f"{key}_speed")
        )
        loss = st.slider(
            "Energy loss per meter (J/m)", 0.0, 500.0, 0.0, 10.0, key=state_key(f"{key}_loss")
        )
        mass = st.slider("Car mass (kg)", 50.0, 1000.0, 200.0, 25.0, key=state_key(f"{key}_mass"))
    return RollerCoasterParameters(mass, start, speed, hill, finish, 80, loss)


def explore():
    mode_heading(LearningMode.EXPLORE, "Can the coaster finish?")
    r = simulate(controls())
    metric_table(
        {
            "Top speed": f"{r.maximum_speed_m_s:.2f} m/s",
            "Energy lost": f"{r.energy_lost_j:.0f} J",
            "Track status": "Complete" if r.completed else "Stops early",
        }
    )
    st.caption("Text outcome: " + r.outcome)
    animation(r, 20262301)
    obs = st.text_input("Optional notebook observation", key=state_key("coaster_obs"))
    if st.button("🎢 Run coaster", type="primary", use_container_width=True):
        record(
            ID,
            r.parameters.to_dict(),
            st.session_state.get(state_key("coaster_quiz_guess")),
            r.outcome,
            numbers(r),
            mission_ui.process_run(ID, evaluate(r)),
            20262301,
            VERSION,
            obs,
        )
        st.rerun()
    mission_ui.mission_checklist("Roller-Coaster Energy")


def compare():
    mode_heading(LearningMode.COMPARE, "Ideal versus dissipative")
    a = simulate(RollerCoasterParameters(loss_per_meter_j=0))
    b = simulate(RollerCoasterParameters(loss_per_meter_j=150))
    changed_variable_banner(ChangedVariable("Dissipative loss", "0 J/m", "150 J/m"))
    metric_table(
        {
            "Ideal top speed": f"{a.maximum_speed_m_s:.2f} m/s",
            "Lossy top speed": f"{b.maximum_speed_m_s:.2f} m/s",
        }
    )
    if st.button("▶ Run energy comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262311), ("Run B", b, 20262312)):
            record(
                ID,
                r.parameters.to_dict(),
                "Losses reduce available mechanical energy",
                r.outcome,
                numbers(r),
                mission_ui.process_run(ID, evaluate(r)),
                seed,
                VERSION,
                None,
                label,
            )
    animation(b, 20262312)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Energy and speed along the track")
    r = simulate(controls("coaster_analysis"))
    distance = list(r.distance_m)
    energy = series_figure(
        x=distance,
        series={
            "Potential energy": list(r.potential_energy_j),
            "Kinetic energy": list(r.kinetic_energy_j),
            "Mechanical energy": list(r.mechanical_energy_j),
        },
        x_label="Distance along track (m)",
        y_label="Energy (J)",
        title="Energy along the modeled track",
    )
    render_chart(
        energy,
        "Potential and kinetic energy trade as height changes. Mechanical energy decreases when loss per meter is nonzero.",
    )
    plt.close(energy)
    speed = series_figure(
        x=distance,
        series={"Speed": list(r.speed_m_s)},
        x_label="Distance along track (m)",
        y_label="Speed (m/s)",
        title="Speed along the modeled track",
    )
    render_chart(
        speed,
        "Speed rises on descents and falls while climbing; the series ends at the first unreachable sample.",
    )
    plt.close(speed)


def model():
    mode_heading(LearningMode.MODEL, "Energy determines reachable track")
    st.latex(r"E=mgh+\frac12mv^2\qquad E(x)=E_0-Lx")
    st.markdown(
        "A track point is physically unreachable when the energy remaining after losses is less than its gravitational potential energy."
    )
    assumptions_panel(
        (
            ModelAssumption("particle", "Car represented as a point mass"),
            ModelAssumption("loss", "Optional loss is constant per meter"),
        ),
        (
            "No wheel rotation.",
            "No aerodynamic speed dependence.",
            "Track curvature does not add losses.",
        ),
    )


def render():
    st.header("🎢 Roller-Coaster Energy")
    revealed = mission_ui.prediction_quiz(
        key=state_key("coaster_quiz"),
        question="As a coaster rolls downhill without losses, what happens to its gravitational potential energy?",
        options=["It becomes kinetic energy", "It disappears", "It stays unchanged"],
        correct_index=0,
        reveal_text="Potential energy decreases while kinetic energy and speed increase.",
        mission_id="coaster_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key=state_key("coaster_mode"))
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
