from physics_playground.canvas.diffusion_player import build_diffusion_document


def test_diffusion_player_is_shared_responsive_and_accessible() -> None:
    document = build_diffusion_document(
        paths=(((0.0, 0.0), (1.0, 1.0)),),
        dimensions=2,
        extent=2,
        message="Seeded walk complete",
        seed=7,
    )
    for token in (
        "AnimationPlayer",
        'id="play-pause"',
        'id="scrubber"',
        "ResizeObserver",
        "devicePixelRatio",
        "prefers-reduced-motion",
        "Particle trajectories",
        "2-dimensional random-walk trajectories",
        "Seeded walk complete",
    ):
        assert token in document
