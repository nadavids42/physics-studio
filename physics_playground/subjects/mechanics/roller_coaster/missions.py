from physics_playground.contracts import MissionEvaluation
def evaluate(r):return (MissionEvaluation("coaster_complete",r.completed,"Track completed"),MissionEvaluation("coaster_fast",r.maximum_speed_m_s>=20,"Reached 20 m/s"),MissionEvaluation("coaster_loss_compare",r.parameters.loss_per_meter_j>0 and r.completed,"Completed with losses"))
