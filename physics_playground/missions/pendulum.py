from physics_playground.contracts import MissionEvaluation
from physics_playground.models.pendulum import PendulumResult
from physics_playground.units import MOON_GRAVITY_M_S2


def evaluate_pendulum_missions(r: PendulumResult):
    return (
        MissionEvaluation("pend_four", 3.9 <= r.period_s <= 4.1, "Build a four-second pendulum."),
        MissionEvaluation(
            "pend_moon",
            abs(r.parameters.gravity_m_s2 - MOON_GRAVITY_M_S2) < 0.01,
            "Swing on the Moon.",
        ),
    )
