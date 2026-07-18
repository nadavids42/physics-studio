import json
import math
from pathlib import Path

import pytest

from physics_playground.canvas.diffusion_player import (SCENE, VISIBLE_WINDOW_SEGMENTS,
                                                         build_diffusion_document)
from physics_playground.subjects.fluids_and_matter.diffusion.page import distribution_bins
from physics_playground.subjects.fluids_and_matter.diffusion.physics import (DiffusionParameters,
                                                                             WalkDimension,
                                                                             simulate)


def test_seeded_trajectories_remain_identical():
    parameters = DiffusionParameters(particle_count=120, steps=90, seed=731)
    first = simulate(parameters)
    second = simulate(parameters)
    assert first.sample_trajectories == second.sample_trajectories
    assert first.final_x_m == second.final_x_m and first.final_y_m == second.final_y_m


def test_display_optimization_does_not_modify_path_arrays():
    paths = (((0.0, 0.0), (1.0, .5), (2.0, 1.0)),)
    before = tuple(tuple(tuple(point) for point in path) for path in paths)
    payload = build_diffusion_document(paths=paths, dimensions=2, extent=3, message="done", seed=1)
    assert paths == before
    assert '"paths":[[[0.0,0.0],[1.0,0.5],[2.0,1.0]]]' in payload


def test_path_drawing_work_is_bounded_and_trails_fade():
    assert VISIBLE_WINDOW_SEGMENTS == 48
    assert "start=Math.max(0,last-c.visibleWindowSegments)" in SCENE
    assert "for(let i=start+1;i<=last;i++)" in SCENE
    assert "ctx.globalAlpha=.12+.68*progress" in SCENE
    payload = build_diffusion_document(paths=(tuple((float(i), 0.) for i in range(500)),),
                                       dimensions=1, extent=500, message="done", seed=2)
    assert '"visibleWindowSegments":48' in payload
    assert '"frameCount":500' in payload


def test_distribution_bins_are_counts_over_meter_widths():
    centers, counts, width = distribution_bins((-1., -.9, 0., .1, .9, 1.), bin_count=4)
    assert len(centers) == len(counts) == 4
    assert sum(counts) == 6
    assert width == pytest.approx(.5)
    assert centers == pytest.approx((-.75, -.25, .25, .75))


def test_theoretical_msd_has_square_meter_units_and_correct_dimension_factor():
    for dimension in (WalkDimension.ONE_D, WalkDimension.TWO_D):
        p = DiffusionParameters(dimensions=dimension, step_size_m=.2, timestep_s=.5,
                                steps=100, particle_count=100, seed=8)
        result = simulate(p)
        expected = 2 * int(dimension) * result.diffusion_coefficient_m2_s * result.elapsed_time_s
        assert expected == pytest.approx(p.steps * p.step_size_m**2)
    page = (Path(__file__).parents[1] / "physics_playground/subjects/fluids_and_matter/diffusion/page.py").read_text()
    assert 'y_label="Mean-squared displacement (m²)"' in page


def test_trajectory_identity_uses_numbers_line_styles_and_markers_not_only_color():
    for token in ("dashes=[", "T${j+1}", "'dashed':'solid'", "ctx.rect(ox-3",
                  "PhysicsAssets.mass"):
        assert token in SCENE


def test_one_and_two_dimensional_presentations_are_distinct_and_labeled():
    path = (((0., 0.), (1., 1.)),)
    one = build_diffusion_document(paths=path, dimensions=1, extent=2, message="one", seed=3)
    two = build_diffusion_document(paths=path, dimensions=2, extent=2, message="two", seed=3)
    assert "1-dimensional random-walk trajectories" in one
    assert "2-dimensional random-walk trajectories" in two
    assert "if(c.dimensions===2)PhysicsAssets.grid" in SCENE
    assert "c.dimensions===2?a[1]:0" in SCENE and "c.dimensions===2?current[1]:0" in SCENE


def test_diffusion_charts_use_binned_histogram_and_shared_msd_system():
    source = (Path(__file__).parents[1] / "physics_playground/subjects/fluids_and_matter/diffusion/page.py").read_text()
    assert "axis.bar(centers,counts,width=width*.9" in source
    assert "series_figure(" in source and "render_chart" in source
    assert "st.bar_chart" not in source and "st.line_chart" not in source
