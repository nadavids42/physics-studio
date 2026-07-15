import pytest
from physics_playground.subjects.waves_and_oscillations.doppler_effect.physics import DopplerParameters,MotionOutcome,simulate
from physics_playground.validation import PhysicsValidationError
def test_stationary_source_and_observer_have_no_shift():
    r=simulate(DopplerParameters());assert r.observed_frequency_hz==pytest.approx(440);assert r.motion is MotionOutcome.UNCHANGED
def test_approaching_source_raises_frequency():
    r=simulate(DopplerParameters(source_velocity_m_s=50));assert r.observed_frequency_hz>r.parameters.source_frequency_hz;assert r.motion is MotionOutcome.APPROACHING
def test_receding_source_lowers_frequency():
    r=simulate(DopplerParameters(source_velocity_m_s=-50));assert r.observed_frequency_hz<r.parameters.source_frequency_hz;assert r.motion is MotionOutcome.RECEDING
def test_observer_moving_toward_source_raises_frequency():assert simulate(DopplerParameters(observer_velocity_m_s=-50)).observed_frequency_hz>440
def test_observer_moving_away_lowers_frequency():assert simulate(DopplerParameters(observer_velocity_m_s=50)).observed_frequency_hz<440
def test_formula_matches_classical_doppler_equation():
    p=DopplerParameters(500,340,40,-20);assert simulate(p).observed_frequency_hz==pytest.approx(500*(340+20)/(340-40))
def test_source_compresses_wavelength_ahead():
    r=simulate(DopplerParameters(source_velocity_m_s=40));assert r.wavelength_ahead_m<343/440<r.wavelength_behind_m
def test_wavefront_frames_are_repeatable_and_expand():
    a=simulate(DopplerParameters());b=simulate(DopplerParameters());assert a==b;assert a.frames[-1].radii_m[0]>a.frames[1].radii_m[0]
@pytest.mark.parametrize("p",[DopplerParameters(source_frequency_hz=0),DopplerParameters(speed_of_sound_m_s=0),DopplerParameters(source_velocity_m_s=343),DopplerParameters(observer_velocity_m_s=-343),DopplerParameters(initial_observer_position_m=0),DopplerParameters(duration_s=-1),DopplerParameters(samples=1),DopplerParameters(source_velocity_m_s=float('nan'))])
def test_invalid_and_extreme_parameters(p):
    with pytest.raises(PhysicsValidationError):simulate(p)
