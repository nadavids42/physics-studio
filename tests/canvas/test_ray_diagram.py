from physics_playground.canvas.ray_diagram import build_ray_diagram
def test_ray_diagram_uses_shared_accessible_responsive_player():
    doc=build_ray_diagram(rays=[{"x1":-1,"y1":1,"x2":0,"y2":0,"label":"Ray","kind":"ray"}],message="Ray result",seed=3,interface=True)
    for token in ("AnimationPlayer",'id="play-pause"','id="scrubber"',"ResizeObserver","devicePixelRatio","prefers-reduced-motion","Geometric ray diagram"):assert token in doc
    assert "setLineDash" in doc
