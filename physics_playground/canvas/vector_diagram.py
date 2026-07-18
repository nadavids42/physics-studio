"""Reusable shared-player diagram for vector cross-product direction."""

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.visual.vectors import VectorScaleMode, VectorSpec

SCENE = load_javascript_asset("scene-vector-diagram.js")


def build_vector_direction_document(
    *,
    motion: tuple[float, float],
    field: tuple[float, float],
    force_z: float,
    motion_label: str,
    message: str,
    seed: int,
    subject_kind: str = "charge",
    charge_sign: float = 1.0,
    guidance: str = "Curl from the motion vector toward the magnetic-field vector.",
) -> str:
    vectors = [
        VectorSpec(
            0,
            0,
            motion[0],
            motion[1],
            "velocity",
            motion_label,
            VectorScaleMode.NORMALIZED,
            fixed_length_px=105,
        ).to_dict(),
        VectorSpec(
            0,
            0,
            field[0],
            field[1],
            "magnetic_field",
            "Magnetic field B",
            VectorScaleMode.NORMALIZED,
            fixed_length_px=105,
        ).to_dict(),
    ]
    config = {
        "durationMs": 1400,
        "autoplay": False,
        "seed": seed,
        "tracks": [{"id": "vector-reveal", "label": "Vector direction reveal", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "vectorDiagram": {
            "vectors": vectors,
            "forceZ": force_z,
            "forceLabel": "Force: out of screen ⊙"
            if force_z > 0
            else ("Force: into screen ⊗" if force_z < 0 else "Force: zero"),
            "subjectKind": subject_kind,
            "chargeSign": charge_sign,
            "guidance": guidance,
        },
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=720,
        logical_height=430,
        accessible_label="Magnetic cross-product vector diagram. " + message,
        idle_hint="Press Play to reveal the vectors and force direction",
    )
