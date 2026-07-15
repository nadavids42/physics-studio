from physics_playground.contracts import MissionEvaluation
from physics_playground.models.spring import SpringResult


def evaluate_boing_missions(result:SpringResult)->tuple[MissionEvaluation,...]:
    p=result.parameters
    return (
        MissionEvaluation("spring_two_second",1.9<=result.period_s<=2.1,"Build a two-second oscillator."),
        MissionEvaluation("spring_fast",result.period_s<.5,"Build an oscillator with a period under half a second."),
        MissionEvaluation("spring_resonance",p.drive_force_n>0 and .9<=p.drive_frequency_ratio<=1.1 and result.late_response_amplitude_m>abs(p.initial_displacement_m)*1.5,
                          "Drive close to the natural frequency and produce a large response."),
    )
