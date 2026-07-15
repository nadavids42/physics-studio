from physics_playground.contracts import MissionEvaluation
from physics_playground.models.double_pendulum import DoublePendulumResult
def evaluate_double_missions(r:DoublePendulumResult):
    theta2=r.plots[5].series[0].x
    return (MissionEvaluation("chaos_diverge",r.final_cartesian_separation_m>.5,"Watch nearly identical systems separate."),MissionEvaluation("chaos_flip",max(abs(v) for v in theta2)>3.14159,"Make the second arm flip around."))
