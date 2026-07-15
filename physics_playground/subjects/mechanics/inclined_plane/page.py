import math
import streamlit as st
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,changed_variable_banner,ChangedVariable,assumptions_panel
from physics_playground.contracts import ModelAssumption
from physics_playground.subjects.mechanics.canvas import document
from physics_playground.subjects.mechanics.ui import show,record,metric_table
from .physics import InclinedPlaneParameters,simulate
from .missions import evaluate
ID="inclined_plane";VERSION="inclined-plane-1.0"
def params(prefix="incline"):
    c1,c2=st.columns(2)
    with c1:m=st.slider("Block mass (kg)",.2,20.0,2.0,.2,key=f"{prefix}_mass");a=st.slider("Ramp angle (degrees)",0,75,30,key=f"{prefix}_angle")
    with c2:mus=st.slider("Static friction coefficient",0.,1.5,.3,.05,key=f"{prefix}_mus");ratio=st.slider("Kinetic friction as a fraction of static friction",0.,1.,.67,.01,key=f"{prefix}_muk_ratio");muk=mus*ratio
    return InclinedPlaneParameters(m,a,mus,muk)
def metrics(r):return {"Acceleration":f"{r.acceleration_m_s2:.2f} m/s²","Normal force":f"{r.normal_force_n:.2f} N","Final speed":f"{r.final_speed_m_s:.2f} m/s"}
def numeric(r):return {"acceleration_m_s2":r.acceleration_m_s2,"normal_force_n":r.normal_force_n,"friction_force_n":r.friction_force_n,"final_speed_m_s":r.final_speed_m_s,"critical_angle_deg":r.critical_angle_deg}
def animate(r,seed,autoplay=True):
    end=1 if r.moving else 0;show(document("ramp",[{"id":"block","label":"Block","x":[0,end],"style":{"color":"#FB8C00"}}],message=r.outcome,seed=seed,autoplay=autoplay))
def explore():
    mode_heading(LearningMode.EXPLORE,"Will it slide?");r=simulate(params());metric_table(metrics(r));st.caption("Text outcome: "+r.outcome);animate(r,20262001,False);obs=st.text_input("Optional notebook observation",key="incline_obs")
    if st.button("▶ Run ramp",type="primary",use_container_width=True):
        badges=kidtools.process_run(ID,evaluate(r));record(ID,r.parameters.to_dict(),st.session_state.get("incline_quiz_guess"),r.outcome,numeric(r),badges,20262001,VERSION,obs);st.rerun()
    kidtools.mission_checklist("Inclined Plane")
def compare():
    mode_heading(LearningMode.COMPARE,"Smooth versus rough");angle=st.slider("Comparison ramp angle",5,70,35);a=simulate(InclinedPlaneParameters(angle_deg=angle,static_friction=.1,kinetic_friction=.05));b=simulate(InclinedPlaneParameters(angle_deg=angle,static_friction=.7,kinetic_friction=.5));changed_variable_banner(ChangedVariable("Friction","Low","High"));metric_table({"Run A acceleration":f"{a.acceleration_m_s2:.2f} m/s²","Run B acceleration":f"{b.acceleration_m_s2:.2f} m/s²"})
    if st.button("▶ Run comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20262011),("Run B",b,20262012)):record(ID,r.parameters.to_dict(),"Lower friction slides faster",r.outcome,numeric(r),kidtools.process_run(ID,evaluate(r)),seed,VERSION,None,label)
    animate(b,20262012,False)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Forces and slipping threshold");mu=st.slider("Static friction for scan",0.,1.2,.3,.05);angles=list(range(0,76,5));values=[simulate(InclinedPlaneParameters(angle_deg=a,static_friction=mu,kinetic_friction=min(.2,mu))).acceleration_m_s2 for a in angles];st.line_chart({"angle_deg":angles,"acceleration_m_s2":values},x="angle_deg",y="acceleration_m_s2");st.caption("Accessible chart description: acceleration remains zero below the slipping threshold, then rises with ramp angle.")
def model():
    mode_heading(LearningMode.MODEL,"Resolve gravity along the ramp");st.latex(r"N=mg\cos\theta\quad F_\parallel=mg\sin\theta");st.latex(r"F_{s,max}=\mu_sN\quad a=g(\sin\theta-\mu_k\cos\theta)");assumptions_panel((ModelAssumption("point","Rigid block and ramp"),ModelAssumption("constant","Constant friction coefficients")),("No air resistance.","The ramp does not deform.","Friction changes instantly from static to kinetic."))
def render():
    st.header("📐 Inclined Plane with Friction");revealed=kidtools.prediction_quiz(key="incline_quiz",question="If a ramp gets steeper while friction stays the same, is the block more likely to slide?",options=["Yes","No","Mass alone decides"],correct_index=0,reveal_text="The downhill part of gravity grows relative to the normal force.",mission_id="incline_predict")
    if not revealed:return
    mode=mode_navigation(key="incline_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
