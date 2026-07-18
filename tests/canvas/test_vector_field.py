from physics_playground.canvas.vector_field import build_vector_field_document


def test_vector_field_player_is_accessible_responsive_and_bounded():
    doc = build_vector_field_document(
        samples=[{"x": 0, "y": 0, "ex": 1, "ey": 0, "v": 2}],
        charges=[{"q": 1, "x": 0, "y": 0}],
        grid_size=1,
        extent=1,
        test_x=0.5,
        test_y=0.5,
        message="Field result",
        seed=5,
    )
    for token in (
        "AnimationPlayer",
        'id="play-pause"',
        'id="scrubber"',
        "ResizeObserver",
        "devicePixelRatio",
        "prefers-reduced-motion",
        "Electric-field vectors and equipotential bands",
    ):
        assert token in doc
    assert "vectorField" in doc and "field-reveal" in doc
