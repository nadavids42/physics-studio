from physics_playground.canvas.gas_container import build_gas_document


def test_gas_container_uses_shared_accessible_player() -> None:
    document = build_gas_document(
        pressure_a_kpa=100,
        pressure_b_kpa=200,
        volume_a_m3=0.024,
        volume_b_m3=0.012,
        temp_a_k=293.15,
        temp_b_k=293.15,
        particles=20,
        message="Compressed gas",
        seed=17,
    )
    for token in (
        "AnimationPlayer", 'id="play-pause"', 'id="scrubber"', "ResizeObserver",
        "devicePixelRatio", "prefers-reduced-motion", "seededRandom",
        "Gas piston changing from state A to state B", "Compressed gas",
    ):
        assert token in document
