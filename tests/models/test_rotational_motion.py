import pytest

from physics_playground.subjects.mechanics.rotational_motion.physics import (
    BodyShape,
    RotationalParameters,
    moment_of_inertia,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_supported_inertia_models():
    assert moment_of_inertia(BodyShape.HOOP, 2, 3) == pytest.approx(18)
    assert moment_of_inertia(BodyShape.SOLID_DISK, 2, 3) == pytest.approx(9)
    assert moment_of_inertia(BodyShape.SOLID_SPHERE, 2, 3) == pytest.approx(7.2)
    assert moment_of_inertia(BodyShape.ROD_CENTER, 2, 3) == pytest.approx(1.5)


def test_torque_equals_inertia_times_angular_acceleration():
    r = simulate(RotationalParameters(torque_n_m=12))
    assert r.moment_of_inertia_kg_m2 * r.angular_acceleration_rad_s2 == pytest.approx(12)


def test_constant_torque_kinematics():
    r = simulate(RotationalParameters(torque_n_m=5, initial_angular_velocity_rad_s=2, duration_s=3))
    assert r.angular_velocity_rad_s[-1] == pytest.approx(2 + r.angular_acceleration_rad_s2 * 3)
    assert r.angular_position_rad[-1] == pytest.approx(
        2 * 3 + 0.5 * r.angular_acceleration_rad_s2 * 9
    )


def test_work_energy_theorem():
    r = simulate(RotationalParameters())
    assert r.work_done_j[-1] == pytest.approx(r.parameters.torque_n_m * r.angular_position_rad[-1])


def test_disk_accelerates_faster_than_hoop():
    disk = simulate(RotationalParameters(shape=BodyShape.SOLID_DISK))
    hoop = simulate(RotationalParameters(shape=BodyShape.HOOP))
    assert disk.angular_acceleration_rad_s2 == pytest.approx(2 * hoop.angular_acceleration_rad_s2)


@pytest.mark.parametrize(
    "p",
    [
        RotationalParameters(mass_kg=0),
        RotationalParameters(radius_or_length_m=0),
        RotationalParameters(duration_s=-1),
        RotationalParameters(samples=1),
        RotationalParameters(torque_n_m=float("inf")),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
