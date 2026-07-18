from physics_playground.canvas.wavefronts import build_wavefront_document


def test_wavefront_player_is_shared_responsive_and_accessible():
    doc = build_wavefront_document(
        frames=[{"source": 0, "observer": 10, "centers": [0], "radii": [0]}],
        world_min=-10,
        world_max=20,
        duration_s=1,
        message="Test result",
        seed=2,
    )
    for token in (
        "AnimationPlayer",
        'id="play-pause"',
        'id="scrubber"',
        "ResizeObserver",
        "devicePixelRatio",
        "prefers-reduced-motion",
        "Animated sound wavefronts",
    ):
        assert token in doc
