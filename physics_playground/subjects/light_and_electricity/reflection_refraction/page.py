import streamlit as st
from physics_playground.canvas import legacy
from physics_playground.canvas.ray_diagram import build_ray_diagram
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.presentation.notebook_ui import add_trial
from .physics import ReflectionRefractionParameters,simulate
from .missions import evaluate
ID="reflection_refraction";VERSION="reflection-refraction-1.0"
def metrics(r):return {"incident_angle_deg":r.parameters.incident_angle_deg,"reflection_angle_deg":r.reflection_angle_deg,"refraction_angle_deg":r.refraction_angle_deg or 0.,"critical_angle_deg":r.critical_angle_deg or 0.,"total_internal_reflection":1. if r.total_internal_reflection else 0.}
def record(r,seed,obs,label=None,badges=()):add_trial(simulation_id=ID,parameters=r.parameters.to_dict(),prediction=st.session_state.get("optics_quiz_guess"),result_summary=r.outcome,metrics=metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def diagram(r,seed):legacy.show(build_ray_diagram(rays=[x.to_dict() for x in r.rays],message=r.outcome,seed=seed,interface=True,bounds=(-5,5,-5,5)),height=500)
def controls(prefix="optics"):
    c=st.columns(3);angle=c[0].slider("Incident angle from normal (°)",0.,89.,35.,1.,key=f"{prefix}_angle");n1=c[1].slider("Medium 1 refractive index",1.,2.5,1.,.01,key=f"{prefix}_n1");n2=c[2].slider("Medium 2 refractive index",1.,2.5,1.5,.01,key=f"{prefix}_n2");return ReflectionRefractionParameters(angle,n1,n2)
def explore():
    mode_heading(LearningMode.EXPLORE,"Send a ray across a boundary");r=simulate(controls());c=st.columns(3);c[0].metric("Reflection angle",f"{r.reflection_angle_deg:.1f}°");c[1].metric("Refraction angle","None — TIR" if r.refraction_angle_deg is None else f"{r.refraction_angle_deg:.1f}°");c[2].metric("Critical angle","N/A" if r.critical_angle_deg is None else f"{r.critical_angle_deg:.1f}°");st.caption("Text outcome: "+r.outcome);diagram(r,20262701);obs=st.text_input("Optional notebook observation",key="optics_obs")
    if st.button("🔦 Trace ray",type="primary",use_container_width=True):record(r,20262701,obs,badges=kidtools.process_run(ID,evaluate(r)));st.rerun()
    kidtools.mission_checklist("Reflection and Refraction")
def compare():
    mode_heading(LearningMode.COMPARE,"Air-to-glass versus glass-to-air");a=simulate(ReflectionRefractionParameters(40,1,1.5));b=simulate(ReflectionRefractionParameters(40,1.5,1));changed_variable_banner(ChangedVariable("Medium order","Air → glass","Glass → air"));c=st.columns(2);c[0].metric("Air → glass",f"{a.refraction_angle_deg:.1f}°");c[1].metric("Glass → air","TIR" if b.refraction_angle_deg is None else f"{b.refraction_angle_deg:.1f}°")
    if st.button("▶ Run index comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20262711),("Run B",b,20262712)):record(r,seed,"Rays bend toward higher refractive index",label,kidtools.process_run(ID,evaluate(r,True)))
    diagram(b,20262712)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Incident angle scan");n1=st.slider("Scan medium 1 index",1.,2.5,1.5,.01);n2=st.slider("Scan medium 2 index",1.,2.5,1.,.01);angles=list(range(0,90));results=[simulate(ReflectionRefractionParameters(a,n1,n2)) for a in angles];st.line_chart({"incident_deg":angles,"reflection_deg":[r.reflection_angle_deg for r in results],"refraction_deg":[r.refraction_angle_deg if r.refraction_angle_deg is not None else float('nan') for r in results]},x="incident_deg",y=["reflection_deg","refraction_deg"]);st.caption("Accessible chart: reflection angle always equals incidence. Refraction bends away from the normal into lower index material and ends at the critical angle when total internal reflection begins.")
def model():
    mode_heading(LearningMode.MODEL,"Reflection and Snell's law");st.latex(r"\theta_r=\theta_i\qquad n_1\sin\theta_1=n_2\sin\theta_2");st.latex(r"\theta_c=\sin^{-1}(n_2/n_1)\quad(n_1>n_2)");assumptions_panel((ModelAssumption("ray","Geometric-optics ray approximation"),ModelAssumption("boundary","Flat boundary between uniform media")),("No wavelength-dependent dispersion.","No absorption or polarization.","Media are isotropic."))
def render():
    st.header("🔦 Reflection and Refraction");revealed=kidtools.prediction_quiz(key="optics_quiz",question="A light ray strikes a mirror at 30° from the normal. What is its reflection angle?",options=["30°","60°","It depends on refractive index"],correct_index=0,reveal_text="The law of reflection says the two angles from the normal are equal.",mission_id="optics_predict")
    if not revealed:return
    mode=mode_navigation(key="optics_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
