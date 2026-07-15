import streamlit as st
from physics_playground.canvas import legacy
from physics_playground.canvas.fluid_container import build_fluid_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.presentation.notebook_ui import add_trial
from .physics import FluidPressureParameters,simulate
from .missions import evaluate
ID="fluid_pressure";VERSION="fluid-pressure-1.0"
def metrics(r):return {"depth_m":r.parameters.depth_m,"gauge_pressure_pa":r.gauge_pressure_pa,"absolute_pressure_pa":r.absolute_pressure_pa,"pressure_gradient_pa_m":r.pressure_increase_per_meter_pa}
def record(r,seed,obs,label=None,badges=()):add_trial(simulation_id=ID,parameters=r.parameters.to_dict(),prediction=st.session_state.get("pressure_quiz_guess"),result_summary=r.outcome,metrics=metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def diagram(r,seed):legacy.show(build_fluid_document(kind="pressure",message=r.outcome,seed=seed,depth=r.parameters.depth_m,maximum_depth=r.parameters.maximum_depth_m),height=570)
def controls(prefix="pressure"):
    c=st.columns(3);density=c[0].slider("Fluid density (kg/m³)",100.,2000.,1000.,25.,key=f"{prefix}_density");maximum=c[1].slider("Container depth (m)",1.,50.,10.,1.,key=f"{prefix}_max");depth=c[2].slider("Measurement depth (m)",0.,float(maximum),min(5.,float(maximum)),.1,key=f"{prefix}_depth");gravity=st.slider("Gravity (m/s²)",1.,25.,9.81,.01,key=f"{prefix}_gravity");surface=st.number_input("Surface pressure (Pa)",min_value=0.,max_value=200000.,value=101325.,step=100.,key=f"{prefix}_surface");return FluidPressureParameters(density,depth,gravity,surface,maximum)
def explore():
    mode_heading(LearningMode.EXPLORE,"Measure pressure below the surface");r=simulate(controls());c=st.columns(3);c[0].metric("Gauge pressure",f"{r.gauge_pressure_pa/1000:.2f} kPa");c[1].metric("Absolute pressure",f"{r.absolute_pressure_pa/1000:.2f} kPa");c[2].metric("Increase per meter",f"{r.pressure_increase_per_meter_pa/1000:.2f} kPa/m");st.caption("Text outcome: "+r.outcome);diagram(r,20263201);obs=st.text_input("Optional notebook observation",key="pressure_obs")
    if st.button("🌊 Measure pressure",type="primary",use_container_width=True):record(r,20263201,obs,badges=kidtools.process_run(ID,evaluate(r)));st.rerun()
    kidtools.mission_checklist("Fluid Pressure")
def compare():
    mode_heading(LearningMode.COMPARE,"Shallow versus deep");a=simulate(FluidPressureParameters(depth_m=2));b=simulate(FluidPressureParameters(depth_m=8));changed_variable_banner(ChangedVariable("Depth","2 m","8 m"));c=st.columns(2);c[0].metric("2 m gauge",f"{a.gauge_pressure_pa/1000:.1f} kPa");c[1].metric("8 m gauge",f"{b.gauge_pressure_pa/1000:.1f} kPa")
    if st.button("▶ Run depth comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20263211),("Run B",b,20263212)):record(r,seed,"Pressure increases linearly with depth",label,kidtools.process_run(ID,evaluate(r,True)))
    diagram(b,20263212)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Compare pressure throughout a column");r=simulate(controls("pressure_analysis"));st.line_chart({"depth_m":[s.depth_m for s in r.samples],"gauge_pressure_kpa":[s.gauge_pressure_pa/1000 for s in r.samples],"absolute_pressure_kpa":[s.absolute_pressure_pa/1000 for s in r.samples]},x="depth_m",y=["gauge_pressure_kpa","absolute_pressure_kpa"]);st.caption("Accessible chart: both pressures increase linearly with depth; absolute pressure is gauge pressure shifted upward by surface pressure.")
def model():
    mode_heading(LearningMode.MODEL,"Hydrostatic pressure");st.latex(r"P_{gauge}=\rho gh,\qquad P_{absolute}=P_{surface}+\rho gh");assumptions_panel((ModelAssumption("static","Fluid is at rest"),ModelAssumption("uniform","Density and gravity are constant")),("No compressibility or density stratification.","No fluid acceleration or surface waves.","Pressure depends on depth, not container shape."))
def render():
    st.header("🌊 Fluid Pressure");revealed=kidtools.prediction_quiz(key="pressure_quiz",question="In a resting fluid, what happens to pressure as depth increases?",options=["It increases","It decreases","Container width decides"],correct_index=0,reveal_text="Each deeper layer supports more fluid above it, adding ρgh.",mission_id="pressure_predict")
    if not revealed:return
    mode=mode_navigation(key="pressure_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
