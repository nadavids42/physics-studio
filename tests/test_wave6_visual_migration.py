import math
from pathlib import Path

import pytest

from physics_playground.canvas.scalar_field import SCENE as FIELD_SCENE, build_scalar_field_document
from physics_playground.canvas.wavefronts import SCENE as WAVEFRONT_SCENE, build_wavefront_document
from physics_playground.subjects.waves_and_oscillations.doppler_effect.physics import DopplerParameters, MotionOutcome, simulate as simulate_doppler
from physics_playground.subjects.waves_and_oscillations.wave_interference.physics import WaveInterferenceParameters, WaveSource, simulate as simulate_waves


def test_resultant_is_exact_existing_pointwise_superposition():
    result = simulate_waves(WaveInterferenceParameters((WaveSource(1.2, 2, 1, .2),
                                                        WaveSource(.7, 3, 2/3, 1.1))))
    for time_index, frame in enumerate(result.superposition_frames):
        for position_index, value in enumerate(frame):
            expected = sum(source[time_index][position_index] for source in result.source_frames)
            assert value == pytest.approx(expected, abs=1e-12)


def test_wave_graph_plane_has_fixed_scale_phase_identity_and_measurements():
    result = simulate_waves(WaveInterferenceParameters())
    payload = build_scalar_field_document(x=result.position_m, frames=result.superposition_frames,
        source_frames=result.source_frames, sources=({"amplitude": 1, "phaseDeg": 0},
        {"amplitude": 1, "phaseDeg": 180}), measurements=({"index": 0},), time_s=result.time_s,
        interference_label="Destructive interference\nΔφ = 180°", duration_s=2,
        accessible_label="waves", completion_message=result.outcome, seed=1)
    assert '"fieldLimit":2' in payload
    assert "const fi=" in FIELD_SCENE and "limit=Math.max(.001,c.fieldLimit||1)" in FIELD_SCENE
    for token in ("PhysicsAssets.grid", "equilibrium", "Source ${i+1}", "Resultant (heavy)",
                  "c.measurements"):
        assert token in FIELD_SCENE
    assert '"phaseDeg":180' in payload and "Destructive interference" in payload


def test_wave_reduced_motion_retains_step_controls_and_static_recorded_frame():
    result = simulate_waves(WaveInterferenceParameters(time_samples=5))
    payload = build_scalar_field_document(x=result.position_m, frames=result.superposition_frames,
        duration_s=2, accessible_label="waves", completion_message="done", seed=2)
    assert 'id="step-back"' in payload and 'id="step-forward"' in payload
    assert '"frameCount":5' in payload
    assert "prefers-reduced-motion" in payload and "frames[fi]" in FIELD_SCENE


def test_doppler_wavefront_payload_preserves_centers_radii_source_and_observer():
    result = simulate_doppler(DopplerParameters(source_velocity_m_s=30, observer_velocity_m_s=-10,
                                                samples=9))
    frames = [{"source": frame.source_position_m, "observer": frame.observer_position_m,
               "centers": frame.centers_m, "radii": frame.radii_m} for frame in result.frames]
    payload = build_wavefront_document(frames=frames, world_min=-700, world_max=800,
        duration_s=2, message=result.outcome, seed=3, source_velocity_m_s=30,
        observer_velocity_m_s=-10, wavelength_ahead_m=result.wavelength_ahead_m,
        wavelength_behind_m=result.wavelength_behind_m, motion_label=result.motion.value)
    last = result.frames[-1]
    assert f'"source":{last.source_position_m}' in payload
    assert f'"observer":{last.observer_position_m}' in payload
    assert f'"centers":[{last.centers_m[0]}' in payload
    assert f'"radii":[{last.radii_m[0]}' in payload


def test_doppler_shared_assets_physical_geometry_and_motion_semantics():
    for token in ("PhysicsAssets.source", "PhysicsAssets.observer", "PhysicsAssets.wavefront",
                  "PhysicsAssets.ruler", "scale_mode:'normalized'", "source ${c.sourceVelocityMps",
                  "observer ${c.observerVelocityMps", "line thickness is decorative"):
        assert token in WAVEFRONT_SCENE
    assert "radius=metersToPixels(frame.radii[i])" in WAVEFRONT_SCENE
    assert "center=map(frame.centers[i])" in WAVEFRONT_SCENE


def test_doppler_sign_convention_matches_approach_recession_labels():
    approaching = simulate_doppler(DopplerParameters(source_velocity_m_s=40))
    receding = simulate_doppler(DopplerParameters(source_velocity_m_s=-40))
    observer_receding = simulate_doppler(DopplerParameters(observer_velocity_m_s=40))
    assert approaching.motion is MotionOutcome.APPROACHING
    assert receding.motion is MotionOutcome.RECEDING
    assert observer_receding.motion is MotionOutcome.RECEDING
    assert approaching.wavelength_ahead_m < approaching.wavelength_behind_m
    assert "compressed ahead" in WAVEFRONT_SCENE and "expanded behind" in WAVEFRONT_SCENE


def test_wave6_pages_route_analysis_charts_through_shared_system():
    root = Path(__file__).parents[1] / "physics_playground/subjects/waves_and_oscillations"
    for simulation in ("wave_interference", "doppler_effect"):
        source = (root / simulation / "page.py").read_text(encoding="utf-8")
        assert "series_figure(" in source and "render_chart" in source
        assert "st.line_chart" not in source
