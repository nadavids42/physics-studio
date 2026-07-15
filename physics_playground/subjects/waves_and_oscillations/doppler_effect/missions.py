from physics_playground.contracts import MissionEvaluation
def evaluate(r,comparison=False):return (MissionEvaluation("doppler_high",r.frequency_ratio>=1.2,"Observed frequency raised by 20%"),MissionEvaluation("doppler_low",r.frequency_ratio<=.8,"Observed frequency lowered by 20%"),MissionEvaluation("doppler_compare",comparison,"Compared approach and recession"))
