import math

import pytest

from physics_playground.subjects.waves_and_oscillations.wave_interference.physics import (
    WaveInterferenceParameters,
    WaveSource,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_constructive_interference_doubles_amplitude():
    r = simulate(WaveInterferenceParameters((WaveSource(), WaveSource())))
    assert max(abs(r.maximum_amplitude), abs(r.minimum_amplitude)) == pytest.approx(2, abs=1e-3)


def test_equal_opposite_phase_waves_cancel():
    r = simulate(WaveInterferenceParameters((WaveSource(), WaveSource(1, 2, 1, math.pi))))
    assert max(abs(r.maximum_amplitude), abs(r.minimum_amplitude)) < 1e-12


def test_superposition_equals_sum_of_source_frames():
    r = simulate(
        WaveInterferenceParameters(
            (WaveSource(1, 2, 1, 0.2), WaveSource(0.5, 1, 2, 0.7), WaveSource(0.2, 3, 1.5, 1.1))
        )
    )
    assert r.superposition_frames[17][42] == pytest.approx(
        sum(frames[17][42] for frames in r.source_frames)
    )


def test_frequency_wavelength_and_speed_relation():
    assert WaveSource(wavelength_m=3, frequency_hz=4).propagation_speed_m_s == pytest.approx(12)


def test_quantitative_displacement_matches_grid_sample():
    r = simulate(WaveInterferenceParameters())
    i = 20
    j = 30
    assert r.displacement_at(r.position_m[j], r.time_s[i]) == pytest.approx(
        r.superposition_frames[i][j]
    )


def test_repeatability():
    p = WaveInterferenceParameters()
    assert simulate(p) == simulate(p)


@pytest.mark.parametrize(
    "p",
    [
        WaveInterferenceParameters((WaveSource(),)),
        WaveInterferenceParameters((WaveSource(amplitude=-1), WaveSource())),
        WaveInterferenceParameters((WaveSource(wavelength_m=0), WaveSource())),
        WaveInterferenceParameters(domain_length_m=0),
        WaveInterferenceParameters(time_samples=1),
        WaveInterferenceParameters(position_samples=10),
        WaveInterferenceParameters((WaveSource(phase_rad=float("nan")), WaveSource())),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
