import pytest

from physics_playground.canvas.player import build_player_document
from physics_playground.canvas.vector_diagram import build_vector_direction_document
from physics_playground.canvas.vector_field import build_vector_field_document
from physics_playground.visual.vectors import (
    CANVAS_VECTOR_JS, DEFAULT_DISCLOSURES, ForceDiagramSpec, VectorScaleMode, VectorSpec,
)


def test_physical_vectors_require_a_quantitative_scale_and_units():
    with pytest.raises(ValueError, match="pixels_per_unit"):
        VectorSpec(0, 0, 3, 4, "velocity")
    with pytest.raises(ValueError, match="units"):
        VectorSpec(0, 0, 3, 4, "velocity", pixels_per_unit=10)
    vector=VectorSpec(0,0,3,4,"velocity",pixels_per_unit=10,units="m/s")
    assert vector.magnitude == 5
    assert vector.scale_disclosure == ""


@pytest.mark.parametrize("mode",[VectorScaleMode.NORMALIZED,VectorScaleMode.SCHEMATIC])
def test_nonphysical_vectors_always_provide_a_scale_disclosure(mode):
    vector=VectorSpec(1,2,1,0,"net_force",scale_mode=mode)
    assert vector.scale_disclosure == DEFAULT_DISCLOSURES[mode]
    assert vector.to_dict()["scale_disclosure"]
    assert vector.to_dict()["scale_mode"] == mode.value


def test_force_diagram_requires_a_shared_origin():
    force=VectorSpec(10,20,0,-9.81,"gravity",pixels_per_unit=4,units="N")
    diagram=ForceDiagramSpec(10,20,(force,))
    assert diagram.to_dict()["vectors"][0]["role"] == "gravity"
    misplaced=VectorSpec(0,0,1,0,"friction",pixels_per_unit=4,units="N")
    with pytest.raises(ValueError,match="share the diagram origin"):
        ForceDiagramSpec(10,20,(misplaced,))


def test_shared_annotation_library_contains_every_required_helper():
    required=("vector","vectorSet","forceDiagram","angleArc","dimensionLine","pathGuide","normalLine",
              "centerOfMass","velocityTrail","motionDirection","disclosure")
    for name in required:assert name in CANVAS_VECTOR_JS
    assert "scale_mode==='physical'" in CANVAS_VECTOR_JS
    assert "Schematic vectors — not drawn to scale" in CANVAS_VECTOR_JS


def test_shared_player_exposes_vector_annotations_to_all_scenes():
    doc=build_player_document(config={"durationMs":1,"tracks":[],"events":[]},scene_javascript="const scene={draw(){}};",
        logical_width=100,logical_height=50,accessible_label="Vectors",idle_hint="Play")
    assert "const PhysicsAnnotations" in doc
    assert "function dimensionLine" in doc


def test_existing_vector_scenes_disclose_normalized_length():
    magnetic=build_vector_direction_document(motion=(1,0),field=(0,1),force_z=1,motion_label="Velocity v",message="Out",seed=1)
    assert '"scale_mode":"normalized"' in magnetic
    assert "vectorSet" in magnetic
    field=build_vector_field_document(samples=[{"x":0,"y":0,"ex":1,"ey":0,"v":2}],charges=[{"q":1,"x":0,"y":0}],
        grid_size=1,extent=1,test_x=.5,test_y=.5,message="Field",seed=1)
    assert "arrow lengths are normalized for visibility" in field
