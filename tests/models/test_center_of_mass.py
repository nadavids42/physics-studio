import pytest
from physics_playground.subjects.mechanics.center_of_mass.physics import CenterOfMassParameters,simulate
from physics_playground.validation import PhysicsValidationError
def test_equal_masses_balance_at_midpoint():assert simulate(CenterOfMassParameters(2,-3,2,3)).center_of_mass_m==pytest.approx(0)
def test_center_moves_toward_heavier_mass():assert simulate(CenterOfMassParameters(1,-2,3,2)).center_of_mass_m==pytest.approx(1)
def test_translation_invariance():
    a=simulate(CenterOfMassParameters(2,-2,3,2));b=simulate(CenterOfMassParameters(2,3,3,7));assert b.center_of_mass_m-a.center_of_mass_m==pytest.approx(5)
def test_zero_mass_object_has_no_effect():
    r=simulate(CenterOfMassParameters(2,-2,2,2,0,100));assert r.center_of_mass_m==pytest.approx(0)
@pytest.mark.parametrize("p",[CenterOfMassParameters(0,0,0,0),CenterOfMassParameters(-1,0,2,1),CenterOfMassParameters(position_1_m=float('nan'))])
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):simulate(p)
