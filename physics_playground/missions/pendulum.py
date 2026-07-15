from physics_playground.contracts import MissionEvaluation
from physics_playground.models.pendulum import PendulumResult
def evaluate_pendulum_missions(r:PendulumResult):
    return (MissionEvaluation("pend_four",3.9<=r.period_s<=4.1,"Build a four-second pendulum."),
            MissionEvaluation("pend_moon",abs(r.parameters.gravity_m_s2-1.62)<.01,"Swing on the Moon."))
