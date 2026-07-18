import pytest

from physics_playground.canvas.fluid_container import SCENE as FLUID_SCENE,build_fluid_document
from physics_playground.canvas.gas_container import SCENE as GAS_SCENE,build_gas_document
from physics_playground.subjects.fluids_and_matter.buoyancy.physics import BuoyancyParameters,BuoyancyState,simulate as simulate_buoyancy
from physics_playground.subjects.fluids_and_matter.fluid_pressure.physics import FluidPressureParameters,simulate as simulate_pressure
from physics_playground.subjects.fluids_and_matter.gas_laws.physics import GasLawParameters,GasLawScenario,simulate as simulate_gas


def test_buoyancy_numerical_states_and_apparent_weight_are_preserved():
    floating=simulate_buoyancy(BuoyancyParameters(object_density_kg_m3=600,fluid_density_kg_m3=1000))
    neutral=simulate_buoyancy(BuoyancyParameters(object_density_kg_m3=1000,fluid_density_kg_m3=1000))
    sinking=simulate_buoyancy(BuoyancyParameters(object_density_kg_m3=1500,fluid_density_kg_m3=1000))
    assert floating.state is BuoyancyState.FLOATING and floating.submerged_fraction==pytest.approx(.6)
    assert floating.apparent_weight_n==0
    assert neutral.state is BuoyancyState.NEUTRAL and neutral.submerged_fraction==1
    assert sinking.state is BuoyancyState.SINKING and sinking.submerged_fraction==1
    assert sinking.apparent_weight_n==pytest.approx(sinking.weight_n-sinking.buoyant_force_n)


def test_buoyancy_scene_uses_shared_assets_measurements_and_declared_force_semantics():
    for token in ("PhysicsAssets.fluidContainer","PhysicsAssets.fluidSurface","PhysicsAssets.block",
                  "PhysicsAnnotations.dimensionLine","PhysicsAnnotations.vectorSet","scale_mode:'normalized'",
                  "PhysicsAnimation.impactRipple"):
        assert token in FLUID_SCENE
    assert "cy=bottom-objectH/2-8" in FLUID_SCENE
    document=build_fluid_document(kind="buoyancy",message="Sinking",seed=1,submerged_fraction=1,state="Sinking",
        object_density=1500,fluid_density=1000,displaced_volume=.01,weight=147.15,buoyant_force=98.1)
    assert '"state":"Sinking"' in document
    assert '"fraction":1' in document
    assert "Force Diagram" not in document


def test_pressure_numerical_samples_and_absolute_offset_are_preserved():
    result=simulate_pressure(FluidPressureParameters(fluid_density_kg_m3=1000,depth_m=5,gravity_m_s2=9.81,surface_pressure_pa=101325,maximum_depth_m=10,samples=21))
    assert result.gauge_pressure_pa==pytest.approx(49050)
    assert result.absolute_pressure_pa==pytest.approx(150375)
    assert [sample.depth_m for sample in result.samples]==pytest.approx([i*.5 for i in range(21)])
    for sample in result.samples:
        assert sample.absolute_pressure_pa-sample.gauge_pressure_pa==pytest.approx(101325)


def test_pressure_scene_maps_selected_depth_and_uses_normalized_pressure_arrows():
    for token in ("PhysicsAssets.ruler","Selected depth","createLinearGradient","Pressure-arrow lengths are normalized",
                  "Surface:","Gauge:","Absolute:"):
        assert token in FLUID_SCENE
    document=build_fluid_document(kind="pressure",message="Pressure",seed=2,depth=5,maximum_depth=10,
        gauge_pressure=49050,absolute_pressure=150375,surface_pressure=101325,
        pressure_samples=[{"depth":0,"gauge":0},{"depth":5,"gauge":49050},{"depth":10,"gauge":98100}])
    assert '"depth":5' in document and '"maxDepth":10' in document
    assert '"ratio":0.5' in document


def _gas_kwargs(seed=17):
    return dict(pressure_a_kpa=100,pressure_b_kpa=200,volume_a_m3=.024,volume_b_m3=.012,
        temp_a_k=293.15,temp_b_k=293.15,particles=20,message="Compressed",seed=seed,amount_mol=1.)


def test_gas_state_values_are_unchanged_by_decorative_document_building():
    result=simulate_gas(GasLawParameters(GasLawScenario.BOYLE,target_volume_m3=.012))
    before=(result.state_a.pressure_pa,result.state_a.volume_m3,result.state_a.temperature_k,
            result.state_b.pressure_pa,result.state_b.volume_m3,result.state_b.temperature_k)
    build_gas_document(pressure_a_kpa=result.state_a.pressure_pa/1000,pressure_b_kpa=result.state_b.pressure_pa/1000,
        volume_a_m3=result.state_a.volume_m3,volume_b_m3=result.state_b.volume_m3,temp_a_k=result.state_a.temperature_k,
        temp_b_k=result.state_b.temperature_k,particles=20,message=result.outcome,seed=3,amount_mol=result.state_a.amount_mol)
    after=(result.state_a.pressure_pa,result.state_a.volume_m3,result.state_a.temperature_k,
           result.state_b.pressure_pa,result.state_b.volume_m3,result.state_b.temperature_k)
    assert after==before
    assert result.state_b.pressure_pa==pytest.approx(2*result.state_a.pressure_pa)


def test_gas_particle_layout_is_precomputed_seeded_and_stable():
    first=build_gas_document(**_gas_kwargs(17));again=build_gas_document(**_gas_kwargs(17));different=build_gas_document(**_gas_kwargs(18))
    assert first==again and first!=different
    assert '"particleLayout":[' in first
    assert "seededRandom(c.seed" not in GAS_SCENE
    assert "c.particleLayout" in GAS_SCENE


def test_gas_scene_uses_shared_assets_piston_volume_mapping_and_reduced_motion_final_state():
    for token in ("PhysicsAssets.fluidContainer","PhysicsAssets.block","v/maxV","s.reducedMotion?1:s.fraction",
                  "Pressure indicators are normalized","Particles are illustrative","not molecular scale"):
        assert token in GAS_SCENE
    assert "createLinearGradient" not in GAS_SCENE


def test_wave2_pages_use_shared_charts_and_separate_incompatible_buoyancy_units():
    from physics_playground.subjects.fluids_and_matter.buoyancy import page as buoyancy_page
    from physics_playground.subjects.fluids_and_matter.fluid_pressure import page as pressure_page
    from physics_playground.subjects.fluids_and_matter.gas_laws import page as gas_page
    sources={module.__name__:open(module.__file__,encoding="utf-8").read() for module in (buoyancy_page,pressure_page,gas_page)}
    assert sources[buoyancy_page.__name__].count("series_figure(")>=2
    for source in sources.values():
        assert "render_chart" in source
        assert "st.line_chart" not in source
