import math
import pytest
from physics_playground.subjects.light_and_electricity.reflection_refraction.physics import ReflectionRefractionParameters,simulate
from physics_playground.validation import PhysicsValidationError
def test_law_of_reflection():
    for angle in (0,10,35,80):assert simulate(ReflectionRefractionParameters(angle)).reflection_angle_deg==pytest.approx(angle)
def test_snells_law():
    p=ReflectionRefractionParameters(40,1,1.5);r=simulate(p);assert p.refractive_index_1*math.sin(math.radians(p.incident_angle_deg))==pytest.approx(p.refractive_index_2*math.sin(math.radians(r.refraction_angle_deg)))
def test_ray_bends_toward_normal_entering_higher_index():assert simulate(ReflectionRefractionParameters(45,1,1.5)).refraction_angle_deg<45
def test_total_internal_reflection_and_critical_angle():
    r=simulate(ReflectionRefractionParameters(50,1.5,1));assert r.total_internal_reflection and r.refraction_angle_deg is None;assert r.critical_angle_deg==pytest.approx(math.degrees(math.asin(1/1.5)))
def test_below_critical_angle_transmits():assert not simulate(ReflectionRefractionParameters(40,1.5,1)).total_internal_reflection
def test_equal_indices_do_not_bend():assert simulate(ReflectionRefractionParameters(63,1.2,1.2)).refraction_angle_deg==pytest.approx(63)
@pytest.mark.parametrize("p",[ReflectionRefractionParameters(-1),ReflectionRefractionParameters(90),ReflectionRefractionParameters(refractive_index_1=0),ReflectionRefractionParameters(refractive_index_2=-1),ReflectionRefractionParameters(incident_angle_deg=float('nan'))])
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):simulate(p)
