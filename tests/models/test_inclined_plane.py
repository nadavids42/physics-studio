import math
import pytest
from physics_playground.subjects.mechanics.inclined_plane.physics import InclinedPlaneParameters,simulate
from physics_playground.validation import PhysicsValidationError
def test_frictionless_acceleration_is_g_sine_theta():
    r=simulate(InclinedPlaneParameters(angle_deg=30,static_friction=0,kinetic_friction=0));assert r.acceleration_m_s2==pytest.approx(9.81*.5)
def test_static_friction_holds_below_critical_angle():
    r=simulate(InclinedPlaneParameters(angle_deg=10,static_friction=.5,kinetic_friction=.3));assert not r.moving and r.acceleration_m_s2==0
def test_mass_does_not_change_acceleration():
    a=simulate(InclinedPlaneParameters(mass_kg=1));b=simulate(InclinedPlaneParameters(mass_kg=10));assert a.acceleration_m_s2==pytest.approx(b.acceleration_m_s2)
@pytest.mark.parametrize("p",[InclinedPlaneParameters(mass_kg=0),InclinedPlaneParameters(angle_deg=90),InclinedPlaneParameters(static_friction=-.1),InclinedPlaneParameters(static_friction=.1,kinetic_friction=.2),InclinedPlaneParameters(angle_deg=float('nan'))])
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):simulate(p)
def test_critical_angle_matches_arctangent():
    r=simulate(InclinedPlaneParameters(static_friction=.5,kinetic_friction=.2));assert r.critical_angle_deg==pytest.approx(math.degrees(math.atan(.5)))
