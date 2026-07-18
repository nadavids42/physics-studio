import streamlit as st
import matplotlib.pyplot as plt
from physics_playground.canvas import legacy
from physics_playground.canvas.vector_diagram import build_vector_direction_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.presentation.accessibility import render_chart
from physics_playground.presentation.chart_system import series_figure
from .physics import ForceMode,MagneticForceParameters,simulate
from .missions import evaluate
ID="magnetic_forces";VERSION="magnetic-force-1.0"
def metrics(r):return {"force_z_n":r.force_z_n,"force_magnitude_n":r.force_magnitude_n,"relative_angle_deg":r.relative_angle_deg,"sine_factor":r.sine_factor,"charge_c":r.parameters.charge_c,"current_a":r.parameters.current_a,"magnetic_field_t":r.parameters.magnetic_field_t}
def record(r,seed,obs,label=None,badges=()):add_trial(simulation_id=ID,parameters=r.parameters.to_dict(),prediction=st.session_state.get("magnetic_quiz_guess"),result_summary=r.outcome,metrics=metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def diagram(r,seed):legacy.show(build_vector_direction_document(motion=r.motion_vector,field=r.field_vector,force_z=r.force_z_n,motion_label="Velocity v" if r.mode is ForceMode.POINT_CHARGE else "Current I",message=r.outcome,seed=seed,subject_kind="charge" if r.mode is ForceMode.POINT_CHARGE else "wire",charge_sign=r.parameters.charge_c if r.mode is ForceMode.POINT_CHARGE else r.parameters.current_a,guidance=r.right_hand_guidance),height=500)
def controls(prefix="magnetic"):
    mode=ForceMode(st.radio("Experiment",[x.value for x in ForceMode],horizontal=True,key=f"{prefix}_experiment"));c1,c2=st.columns(2)
    with c1:
        charge_micro=st.slider("Charge (µC)",-10.,10.,1.,.1,key=f"{prefix}_q",disabled=mode is ForceMode.CURRENT_WIRE);speed=st.slider("Charge speed (m/s)",0.,500.,100.,5.,key=f"{prefix}_speed",disabled=mode is ForceMode.CURRENT_WIRE);current=st.slider("Current (A)",-20.,20.,2.,.5,key=f"{prefix}_current",disabled=mode is ForceMode.POINT_CHARGE);length=st.slider("Wire length (m)",.05,5.,.5,.05,key=f"{prefix}_length",disabled=mode is ForceMode.POINT_CHARGE)
    with c2:motion=st.slider("Velocity/current direction (°)",-180,180,0,5,key=f"{prefix}_motion");field=st.slider("Magnetic field (T)",0.,5.,.2,.05,key=f"{prefix}_field");field_angle=st.slider("Magnetic-field direction (°)",-180,180,90,5,key=f"{prefix}_field_angle")
    return MagneticForceParameters(mode,charge_micro*1e-6,speed,current,length,motion,field,field_angle)
def explore():
    mode_heading(LearningMode.EXPLORE,"Cross motion or current with a magnetic field");r=simulate(controls());c=st.columns(3);c[0].metric("Force magnitude",f"{r.force_magnitude_n:.3g} N");c[1].metric("Signed z-force",f"{r.force_z_n:+.3g} N");c[2].metric("Direction",r.direction.value);st.caption("Text outcome: "+r.outcome);st.info("Right-hand rule: "+r.right_hand_guidance);diagram(r,20263001);obs=st.text_input("Optional notebook observation",key="magnetic_obs")
    if st.button("🧲 Calculate magnetic force",type="primary",use_container_width=True):record(r,20263001,obs,badges=kidtools.process_run(ID,evaluate(r)));st.rerun()
    kidtools.mission_checklist("Magnetic Forces")
def compare():
    mode_heading(LearningMode.COMPARE,"Perpendicular versus parallel");a=simulate(MagneticForceParameters(motion_angle_deg=0,field_angle_deg=90));b=simulate(MagneticForceParameters(motion_angle_deg=0,field_angle_deg=0));changed_variable_banner(ChangedVariable("Angle between v and B","90°","0°"));c=st.columns(2);c[0].metric("Perpendicular force",f"{a.force_magnitude_n:.3g} N");c[1].metric("Parallel force",f"{b.force_magnitude_n:.3g} N")
    if st.button("▶ Run angle comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20263011),("Run B",b,20263012)):record(r,seed,"Magnetic force depends on sin θ",label,kidtools.process_run(ID,evaluate(r,True)))
    diagram(b,20263012)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Force versus vector angle");mode=ForceMode(st.selectbox("Analysis experiment",[x.value for x in ForceMode]));angles=list(range(0,361,5));results=[simulate(MagneticForceParameters(mode=mode,motion_angle_deg=0,field_angle_deg=a)) for a in angles];figure=series_figure(x=angles,series={"Signed z-force":[r.force_z_n for r in results],"Force magnitude":[r.force_magnitude_n for r in results]},x_label="Angle between vectors (degrees)",y_label="Force (N)",title="Magnetic force versus vector angle");render_chart(figure,"Force is zero for parallel and antiparallel vectors, reaches maximum magnitude at 90° and 270°, and its signed direction reverses across the screen plane.");plt.close(figure)
def model():
    mode_heading(LearningMode.MODEL,"Cross products and the right-hand rule");st.latex(r"\vec F=q\vec v\times\vec B,\qquad |F|=|q|vB|\sin\theta|");st.latex(r"\vec F=I\vec L\times\vec B,\qquad |F|=|I|LB|\sin\theta|");st.markdown("The signed result is the z-component: positive means out of the screen (⊙), negative means into it (⊗). Reverse charge or current reverses force. Parallel vectors have zero cross product.");assumptions_panel((ModelAssumption("uniform","Magnetic field is uniform"),ModelAssumption("element","Wire is straight and fully inside the field")),("No electric field or radiation.","Point charge speed is nonrelativistic.","Wire self-fields and end effects are omitted."))
def render():
    st.header("🧲 Magnetic Forces");revealed=kidtools.prediction_quiz(key="magnetic_quiz",question="A positive charge moves exactly parallel to a magnetic field. What magnetic force acts on it?",options=["Zero","Maximum","It accelerates along the field"],correct_index=0,reveal_text="The cross product contains sin 0° = 0, so parallel motion produces no magnetic force.",mission_id="magnetic_predict")
    if not revealed:return
    mode=mode_navigation(key="magnetic_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
