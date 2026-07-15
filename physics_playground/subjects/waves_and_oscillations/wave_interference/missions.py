from physics_playground.contracts import MissionEvaluation
def evaluate(result,comparison=False):
    total=sum(source.amplitude for source in result.parameters.sources);peak=max(abs(result.maximum_amplitude),abs(result.minimum_amplitude));return (MissionEvaluation("wave_constructive",peak>=.9*total,"Nearly complete constructive interference"),MissionEvaluation("wave_destructive",peak<=.25*total,"Strong cancellation"),MissionEvaluation("wave_phase_compare",comparison,"Compared phase settings"))
