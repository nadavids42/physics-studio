import pytest

from physics_playground.subjects.mechanics.torque_levers.physics import LeverParameters, simulate
from physics_playground.validation import PhysicsValidationError


def test_balanced_torques():
    r = simulate(LeverParameters(200, 0.5, 50, 2))
    assert r.net_torque_n_m == pytest.approx(0)
    assert "balances" in r.outcome


def test_required_force_and_mechanical_advantage():
    r = simulate(LeverParameters(300, 0.4, 0, 2))
    assert r.required_balance_force_n == pytest.approx(60)
    assert r.mechanical_advantage == pytest.approx(5)


def test_zero_force_is_valid():
    assert simulate(LeverParameters(0, 0.5, 0, 1)).net_torque_n_m == 0


@pytest.mark.parametrize(
    "p",
    [
        LeverParameters(load_force_n=-1),
        LeverParameters(load_arm_m=0),
        LeverParameters(effort_arm_m=-1),
        LeverParameters(effort_force_n=float("inf")),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
