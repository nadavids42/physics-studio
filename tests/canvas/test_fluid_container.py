from physics_playground.canvas.fluid_container import build_fluid_document
def test_fluid_container_player_is_accessible_and_responsive():
    buoy=build_fluid_document(kind="buoyancy",message="Floating",seed=1,submerged_fraction=.6);pressure=build_fluid_document(kind="pressure",message="Deep pressure",seed=2,depth=5,maximum_depth=10)
    for doc in (buoy,pressure):
        for token in ("AnimationPlayer",'id="play-pause"','id="scrubber"',"ResizeObserver","devicePixelRatio","prefers-reduced-motion","Fluid container diagram"):assert token in doc
    assert "submerged" in buoy and "Selected depth" in pressure
