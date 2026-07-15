from physics_playground.canvas.scalar_field import build_scalar_field_document
def test_scalar_field_uses_shared_player_and_accessibility_controls():
    document=build_scalar_field_document(x=(0.,1.),frames=((0.,1.),(1.,0.)),duration_s=1,accessible_label="Test wave field",completion_message="Done",seed=4)
    assert "AnimationPlayer" in document and "fieldFrames" in document
    assert 'id="play-pause"' in document and 'id="scrubber"' in document and "ResizeObserver" in document
    assert "Test wave field" in document and "devicePixelRatio" in document and "prefers-reduced-motion" in document
