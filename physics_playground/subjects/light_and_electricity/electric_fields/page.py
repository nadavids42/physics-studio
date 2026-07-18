import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import legacy
from physics_playground.canvas.vector_field import build_vector_field_document
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
from physics_playground.presentation.notebook_ui import add_trial

from .missions import evaluate
from .physics import MAX_FIELD_POINTS, ElectricFieldParameters, PointCharge, field_at, simulate

ID = "electric_fields"
VERSION = "electric-field-1.0"


def metrics(r):
    return {
        "test_field_magnitude_n_c": r.test_field_magnitude_n_c,
        "test_potential_v": r.test_potential_v,
        "force_magnitude_n": r.force_magnitude_n,
        "force_x_n": r.force_x_n,
        "force_y_n": r.force_y_n,
        "excluded_grid_points": float(r.excluded_points),
    }


def record(r, seed, obs, label=None, badges=()):
    add_trial(
        simulation_id=ID,
        parameters=r.parameters.to_dict(),
        prediction=st.session_state.get("field_quiz_guess"),
        result_summary=r.outcome,
        metrics=metrics(r),
        earned_badges=badges,
        random_seed=seed,
        model_version=VERSION,
        learner_observation=obs,
        label=label,
    )


def diagram(r, seed):
    samples = [
        {"x": p.x_m, "y": p.y_m, "ex": p.electric_x_n_c, "ey": p.electric_y_n_c, "v": p.potential_v}
        for p in r.samples
    ]
    charges = [{"q": q.charge_c, "x": q.x_m, "y": q.y_m} for q in r.parameters.charges]
    legacy.show(
        build_vector_field_document(
            samples=samples,
            charges=charges,
            grid_size=r.parameters.grid_size,
            extent=r.parameters.extent_m,
            test_x=r.parameters.test_x_m,
            test_y=r.parameters.test_y_m,
            message=r.outcome,
            seed=seed,
            test_charge=r.parameters.test_charge_c,
        ),
        height=690,
    )


def controls(prefix="field"):
    count = st.slider("Number of source charges", 1, 4, 2, key=f"{prefix}_count")
    charges = []
    defaults = ((-1.0, 0.0, 1.0), (1.0, 0.0, -1.0), (0.0, -1.0, 1.0), (0.0, 1.0, -1.0))
    for i in range(count):
        with st.expander(f"Charge {i + 1}", expanded=i < 2):
            c = st.columns(3)
            x = c[0].slider("x position (m)", -3.0, 3.0, defaults[i][0], 0.1, key=f"{prefix}_x{i}")
            y = c[1].slider("y position (m)", -3.0, 3.0, defaults[i][1], 0.1, key=f"{prefix}_y{i}")
            micro = c[2].slider("Charge (µC)", -5.0, 5.0, defaults[i][2], 0.1, key=f"{prefix}_q{i}")
            if micro == 0:
                st.warning("A source charge cannot be zero; choose a positive or negative value.")
            charges.append(PointCharge(micro * 1e-6, x, y))
    c1, c2, c3 = st.columns(3)
    tx = c1.slider("Test-charge x (m)", -3.5, 3.5, 0.0, 0.1, key=f"{prefix}_tx")
    ty = c2.slider("Test-charge y (m)", -3.5, 3.5, 1.0, 0.1, key=f"{prefix}_ty")
    test_micro = c3.slider("Test charge (µC)", -2.0, 2.0, 0.001, 0.001, key=f"{prefix}_tq")
    grid = st.select_slider(
        "Field-grid density",
        options=[17, 21, 25, 29, 33, 37, 41, 45, 49],
        value=25,
        key=f"{prefix}_grid",
    )
    st.caption(
        f"Performance budget: {grid**2:,} of {MAX_FIELD_POINTS:,} maximum field points. Points within 0.12 m of a source are excluded."
    )
    return ElectricFieldParameters(tuple(charges), test_micro * 1e-6, tx, ty, 4.0, grid, 0.12)


def explore():
    mode_heading(LearningMode.EXPLORE, "Arrange charges and probe the field")
    r = simulate(controls())
    c = st.columns(3)
    c[0].metric("Field at test charge", f"{r.test_field_magnitude_n_c:.3g} N/C")
    c[1].metric("Potential", f"{r.test_potential_v:.3g} V")
    c[2].metric("Force", f"{r.force_magnitude_n:.3g} N")
    st.caption("Text outcome: " + r.outcome)
    diagram(r, 20262901)
    obs = st.text_input("Optional notebook observation", key="field_obs")
    if st.button("⚡ Map electric field", type="primary", use_container_width=True):
        record(r, 20262901, obs, badges=kidtools.process_run(ID, evaluate(r)))
        st.rerun()
    kidtools.mission_checklist("Electric Fields")


def compare():
    mode_heading(LearningMode.COMPARE, "Like charges versus a dipole")
    a = simulate(
        ElectricFieldParameters((PointCharge(1e-6, -1, 0), PointCharge(1e-6, 1, 0)), test_y_m=1)
    )
    b = simulate(
        ElectricFieldParameters((PointCharge(1e-6, -1, 0), PointCharge(-1e-6, 1, 0)), test_y_m=1)
    )
    changed_variable_banner(ChangedVariable("Right charge", "+1 µC", "−1 µC"))
    c = st.columns(2)
    c[0].metric("Like-charge field", f"{a.test_field_magnitude_n_c:.2f} N/C")
    c[1].metric("Dipole field", f"{b.test_field_magnitude_n_c:.2f} N/C")
    if st.button("▶ Run field comparison", use_container_width=True):
        for label, r, seed in (("Run A", a, 20262911), ("Run B", b, 20262912)):
            record(
                r,
                seed,
                "Changing one sign reshapes both field and potential",
                label,
                kidtools.process_run(ID, evaluate(r, True)),
            )
    diagram(b, 20262912)


def analyze():
    mode_heading(LearningMode.ANALYZE, "Field and potential along a line")
    r = simulate(controls("field_analysis"))
    xs = [-4 + i * 0.04 for i in range(201)]
    potential = []
    magnitude = []
    for x in xs:
        try:
            ex, ey, v = field_at(
                r.parameters.charges, x, r.parameters.test_y_m, r.parameters.minimum_distance_m
            )
            potential.append(v)
            magnitude.append((ex * ex + ey * ey) ** 0.5)
        except Exception:
            potential.append(None)
            magnitude.append(None)
    potential_figure = series_figure(
        x=xs,
        series={"Electric potential": potential},
        x_label="Position x (m)",
        y_label="Electric potential (V)",
        title="Potential along the selected line",
    )
    render_chart(
        potential_figure,
        "Electric potential is positive near positive charges, negative near negative charges, and omitted inside singularity exclusion zones.",
    )
    plt.close(potential_figure)
    field_figure = series_figure(
        x=xs,
        series={"Field magnitude": magnitude},
        x_label="Position x (m)",
        y_label="Field magnitude (N/C)",
        title="Electric-field magnitude along the selected line",
    )
    render_chart(
        field_figure,
        "Field magnitude grows sharply near charges; excluded gaps prevent singular values from dominating the chart.",
    )
    plt.close(field_figure)


def model():
    mode_heading(LearningMode.MODEL, "Superpose fields and potentials")
    st.latex(r"\vec E(\vec r)=k\sum_i q_i\frac{\vec r-\vec r_i}{|\vec r-\vec r_i|^3}")
    st.latex(r"V(\vec r)=k\sum_i\frac{q_i}{|\vec r-\vec r_i|},\qquad \vec F=q_{test}\vec E")
    st.markdown(
        f"Dense visualizations are capped at **{MAX_FIELD_POINTS:,} samples** and six source charges. Points closer than the selected minimum distance are excluded rather than softened or allowed to become infinite."
    )
    assumptions_panel(
        (
            ModelAssumption("point", "Charges are ideal mathematical points"),
            ModelAssumption("static", "Charges remain fixed in vacuum"),
        ),
        (
            "No magnetic or radiation effects.",
            "No conductors, polarization, or material boundaries.",
            "The minimum-distance exclusion is a numerical visualization safeguard, not a new physical law.",
        ),
    )


def render():
    st.header("⚡ Electric Fields")
    revealed = kidtools.prediction_quiz(
        key="field_quiz",
        question="Which direction does the electric field point near a positive source charge?",
        options=["Away from it", "Toward it", "Clockwise around it"],
        correct_index=0,
        reveal_text="A positive test charge would be pushed away, which defines the field direction.",
        mission_id="field_predict",
    )
    if not revealed:
        return
    mode = mode_navigation(key="field_mode")
    {
        LearningMode.EXPLORE: explore,
        LearningMode.COMPARE: compare,
        LearningMode.ANALYZE: analyze,
        LearningMode.MODEL: model,
    }[mode]()
