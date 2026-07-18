import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import embed
from physics_playground.canvas.ray_diagram import build_ray_diagram
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
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.state_keys import simulation_key

from .missions import evaluate
from .physics import ThinLensParameters, simulate

ID = "thin_lenses"


def state_key(name: str) -> str:
    canonical = simulation_key(ID, name)
    if name in st.session_state and canonical not in st.session_state:
        st.session_state[canonical] = st.session_state.pop(name)
    return canonical


VERSION = "thin-lens-1.0"


def metrics(r):
    return {
        "object_distance_m": r.parameters.object_distance_m,
        "focal_length_m": r.parameters.focal_length_m,
        "image_distance_m": r.image_distance_m or 0.0,
        "magnification": r.magnification or 0.0,
        "image_height_m": r.image_height_m or 0.0,
        "real_image": 1.0 if r.real_image else 0.0,
        "singular": 1.0 if r.singular else 0.0,
    }


def record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id=ID,
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get(state_key("lens_quiz_guess")),
        result_summary=r.outcome,
        metrics=metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def diagram(r, seed):
    span = max(5.0, min(15.0, r.parameters.object_distance_m, abs(r.image_distance_m or 5)) * 1.2)
    embed.show(
        build_ray_diagram(
            rays=[x.to_dict() for x in r.rays],
            message=r.outcome,
            seed=seed,
            lens=True,
            lens_sign=1 if r.parameters.focal_length_m > 0 else -1,
            bounds=(-span, span, -5, 5),
        ),
        height=500,
    )


def controls(prefix="lens"):
    c = st.columns(3)
    do = c[0].slider("Object distance (m)", 0.1, 10.0, 3.0, 0.05, key=state_key(f"{prefix}_do"))
    kind = c[1].radio("Lens type", ["Converging", "Diverging"], key=state_key(f"{prefix}_kind"))
    magnitude = c[2].slider(
        "Focal-length magnitude (m)", 0.1, 5.0, 1.0, 0.05, key=state_key(f"{prefix}_f")
    )
    return ThinLensParameters(do, magnitude if kind == "Converging" else -magnitude, 1.0)


def explore():
    mode_heading(LearningMode.EXPLORE, "Form an image")
    r = simulate(controls())
    c = st.columns(3)
    c[0].metric(
        "Image distance", "∞" if r.image_distance_m is None else f"{r.image_distance_m:.2f} m"
    )
    c[1].metric(
        "Magnification", "Undefined" if r.magnification is None else f"{r.magnification:.2f}×"
    )
    c[2].metric(
        "Image type",
        "At infinity" if r.singular else ("Real, inverted" if r.real_image else "Virtual, upright"),
    )
    st.caption("Text outcome: " + r.outcome)
    diagram(r, 20262801)
    obs = st.text_input("Optional notebook observation", key=state_key("lens_obs"))
    if st.button("🔍 Trace principal rays", type="primary", use_container_width=True):
        record(r, 20262801, obs, badges=mission_ui.process_run(ID, evaluate(r)))
        st.rerun()
    mission_ui.mission_checklist("Thin Lenses")


def compare():
    mode_heading(LearningMode.COMPARE, "Converging versus diverging")
    a = simulate(ThinLensParameters(3, 1))
    b = simulate(ThinLensParameters(3, -1))
    changed_variable_banner(ChangedVariable("Lens type", "Converging", "Diverging"))
    c = st.columns(2)
    c[0].metric("Converging image", f"{a.image_distance_m:.2f} m")
    c[1].metric("Diverging image", f"{b.image_distance_m:.2f} m")
    if st.button("▶ Run lens comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262811), ("Run B", b, 20262812)):
            record(
                r,
                seed,
                "Lens sign changes real versus virtual behavior",
                label,
                mission_ui.process_run(ID, evaluate(r, True)),
            )
    diagram(b, 20262812)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Image distance near the focal point")
    f = st.slider("Analysis focal length (m)", 0.2, 3.0, 1.0, 0.1)
    distances = [0.1 + i * 0.05 for i in range(200) if abs((0.1 + i * 0.05) - f) > 0.01]
    images = [simulate(ThinLensParameters(d, f)).image_distance_m for d in distances]
    figure = series_figure(
        x=distances,
        series={"Image distance": images},
        x_label="Object distance (m)",
        y_label="Image distance (m)",
        title="Thin-lens response near the focal point",
    )
    render_chart(
        figure,
        "Image distance diverges at object distance equal to focal length, is negative for a virtual image inside the focus, and positive beyond it.",
    )
    plt.close(figure)


def model():
    mode_heading(LearningMode.MODEL, "The signed thin-lens equation")
    st.latex(r"\frac1f=\frac1{d_o}+\frac1{d_i}\qquad m=-\frac{d_i}{d_o}=\frac{h_i}{h_o}")
    st.markdown(
        "Positive focal length means converging; negative means diverging. Positive image distance is real, negative is virtual. Negative magnification is inverted."
    )
    assumptions_panel(
        (
            ModelAssumption("thin", "Lens thickness is negligible"),
            ModelAssumption("paraxial", "Rays remain near the optical axis"),
        ),
        (
            "No aberration or dispersion.",
            "One ideal lens in air.",
            "Near the focal point, tiny input changes produce enormous image-distance changes.",
        ),
    )


def render():
    st.header("🔍 Thin Lenses")
    revealed = mission_ui.prediction_quiz(
        key=state_key("lens_quiz"),
        question="A converging lens has an object beyond its focal point. What kind of image can it form?",
        options=["Real and inverted", "Always virtual", "No image"],
        correct_index=0,
        reveal_text="Principal rays converge on the far side to form a real, inverted image.",
        mission_id="lens_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key=state_key("lens_mode"))
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
