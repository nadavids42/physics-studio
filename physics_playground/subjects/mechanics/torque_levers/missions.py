from physics_playground.contracts import MissionEvaluation
def evaluate(result):
    return (MissionEvaluation("lever_balance",abs(result.net_torque_n_m)<1,"Torques balance"),MissionEvaluation("lever_advantage",result.mechanical_advantage>=3,"Large mechanical advantage"))
