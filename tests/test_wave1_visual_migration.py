import pytest

from physics_playground.canvas.ray_diagram import SCENE as RAY_SCENE
from physics_playground.canvas.ray_diagram import build_ray_diagram
from physics_playground.canvas.vector_diagram import (
    SCENE as VECTOR_SCENE,
)
from physics_playground.canvas.vector_diagram import (
    build_vector_direction_document,
)
from physics_playground.canvas.vector_field import SCENE as FIELD_SCENE
from physics_playground.canvas.vector_field import build_vector_field_document
from physics_playground.subjects.light_and_electricity.magnetic_forces.physics import (
    ForceDirection,
    ForceMode,
    MagneticForceParameters,
)
from physics_playground.subjects.light_and_electricity.magnetic_forces.physics import (
    simulate as simulate_magnetic,
)
from physics_playground.subjects.light_and_electricity.reflection_refraction.physics import (
    ReflectionRefractionParameters,
)
from physics_playground.subjects.light_and_electricity.reflection_refraction.physics import (
    simulate as simulate_optics,
)


def test_optics_numerical_baseline_and_total_internal_reflection_are_preserved():
    ordinary = simulate_optics(ReflectionRefractionParameters(35, 1, 1.5))
    assert ordinary.reflection_angle_deg == 35
    assert ordinary.refraction_angle_deg == pytest.approx(22.4814495355)
    assert len(ordinary.rays) == 3
    tir = simulate_optics(ReflectionRefractionParameters(60, 1.5, 1))
    assert tir.total_internal_reflection is True
    assert tir.refraction_angle_deg is None
    assert len(tir.rays) == 2
    assert all(ray.label != "Refracted ray" for ray in tir.rays)


def test_optics_scene_uses_medium_regions_boundary_normal_angles_and_scale_disclosure():
    for token in (
        "Medium 1",
        "Medium 2",
        "normalLine",
        "angleArc",
        "totalInternalReflection",
        "displayed ray lengths are schematic",
    ):
        assert token in RAY_SCENE
    result = simulate_optics(ReflectionRefractionParameters(60, 1.5, 1))
    document = build_ray_diagram(
        rays=[ray.to_dict() for ray in result.rays],
        message=result.outcome,
        seed=4,
        interface=True,
        medium_1=1.5,
        medium_2=1,
        incident_angle_deg=60,
        refraction_angle_deg=None,
        total_internal_reflection=True,
    )
    assert '"medium1":1.5' in document and '"medium2":1' in document
    assert '"totalInternalReflection":true' in document
    assert "No transmitted ray" in document


def test_magnetic_model_baselines_cover_charge_wire_reversal_and_zero_force():
    positive = simulate_magnetic(MagneticForceParameters(field_angle_deg=90))
    negative = simulate_magnetic(MagneticForceParameters(charge_c=-1e-6, field_angle_deg=90))
    parallel = simulate_magnetic(MagneticForceParameters(field_angle_deg=0))
    wire = simulate_magnetic(
        MagneticForceParameters(
            mode=ForceMode.CURRENT_WIRE,
            current_a=2,
            wire_length_m=0.5,
            magnetic_field_t=0.2,
            field_angle_deg=90,
        )
    )
    assert (
        positive.force_z_n == pytest.approx(2e-5)
        and positive.direction is ForceDirection.OUT_OF_SCREEN
    )
    assert (
        negative.force_z_n == pytest.approx(-2e-5)
        and negative.direction is ForceDirection.INTO_SCREEN
    )
    assert parallel.force_z_n == 0 and parallel.direction is ForceDirection.ZERO
    assert wire.force_z_n == pytest.approx(0.2)


def test_magnetic_scene_uses_typed_normalized_vectors_subject_assets_and_no_false_force_arrow():
    for token in ("PhysicsAssets.charge", "PhysicsAssets.rod", "vectorSet", "Right-hand rule"):
        assert token in VECTOR_SCENE
    document = build_vector_direction_document(
        motion=(1, 0), field=(1, 0), force_z=0, motion_label="Velocity v", message="Zero", seed=2
    )
    assert document.count('"scale_mode":"normalized"') == 2
    assert '"forceLabel":"Force: zero"' in document
    assert "PhysicsAnnotations.forceDiagram" not in VECTOR_SCENE


def test_electric_field_render_inputs_are_precomputed_bounded_and_deterministic():
    samples = [
        {"x": -1, "y": 0, "ex": None, "ey": None, "v": None},
        {"x": 0, "y": 0, "ex": 3.0, "ey": 4.0, "v": -2.0},
        {"x": 1, "y": 0, "ex": 6.0, "ey": 8.0, "v": 5.0},
    ]
    kwargs = dict(
        samples=samples,
        charges=[{"q": 1e-6, "x": 0, "y": 0}],
        grid_size=3,
        extent=1,
        test_x=0.5,
        test_y=0.5,
        test_charge=-1e-9,
        message="Field",
        seed=8,
    )
    first = build_vector_field_document(**kwargs)
    second = build_vector_field_document(**kwargs)
    assert first == second
    assert '"potentialLimit":5.0' in first
    assert '"fieldMagnitudeLimit":10.0' in first
    assert '"excluded":[{"x":-1,"y":0}]' in first
    assert '"samples":[{"x":0,"y":0,"ex":3.0,"ey":4.0,"v":-2.0}' in first
    assert '"testCharge":-1e-09' in first


def test_electric_field_scene_uses_semantic_assets_grid_exclusions_legend_and_disclosure():
    for token in (
        "PhysicsAssets.grid",
        "PhysicsAssets.charge",
        "PhysicsAnnotations.dimensionLine",
        "Hatched: singularity excluded",
        "normalized for visibility using logarithmic magnitude",
        "PhysicsVisuals.responsive",
    ):
        assert token in FIELD_SCENE
    assert ".filter(" not in FIELD_SCENE
    assert "Math.max(1,..." not in FIELD_SCENE


def test_wave1_pages_use_the_shared_chart_system_without_native_line_charts():
    from physics_playground.subjects.light_and_electricity.electric_fields import page as field_page
    from physics_playground.subjects.light_and_electricity.magnetic_forces import (
        page as magnetic_page,
    )
    from physics_playground.subjects.light_and_electricity.reflection_refraction import (
        page as optics_page,
    )

    for module in (field_page, magnetic_page, optics_page):
        source = open(module.__file__, encoding="utf-8").read()
        assert "series_figure" in source and "render_chart" in source
        assert "st.line_chart" not in source
