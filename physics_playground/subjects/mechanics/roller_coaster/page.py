import streamlit as st
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.subjects.mechanics.canvas import document
from physics_playground.subjects.mechanics.ui import show,record,metric_table
from .physics import RollerCoasterParameters,simulate
from .missions import evaluate
ID="roller_coaster";VERSION="roller-coaster-1.0"
def numbers(r):return {"maximum_speed_m_s":r.maximum_speed_m_s,"energy_lost_j":r.energy_lost_j,"final_mechanical_energy_j":r.mechanical_energy_j[-1] if r.mechanical_energy_j else 0.,"stopping_distance_m":r.stopping_distance_m or r.parameters.track_length_m}
def animation(r,seed):
    end=(r.distance_m[-1]/r.parameters.track_length_m) if r.distance_m else 0.;show(document("coaster",[{"id":"car","label":"Coaster","x":[0,end],"style":{"color":"#E53935"}}],message=r.outcome,seed=seed,autoplay=False))
def controls(key="coaster"):
    c1,c2=st.columns(2)
    with c1:start=st.slider("Starting height (m)",1.,50.,20.,1.,key=f"{key}_start");hill=st.slider("Middle hill height (m)",0.,60.,12.,1.,key=f"{key}_hill");finish=st.slider("Final height (m)",0.,40.,2.,1.,key=f"{key}_finish")
    with c2:speed=st.slider("Starting speed (m/s)",0.,25.,0.,.5,key=f"{key}_speed");loss=st.slider("Energy loss per meter (J/m)",0.,500.,0.,10.,key=f"{key}_loss");mass=st.slider("Car mass (kg)",50.,1000.,200.,25.,key=f"{key}_mass")
    return RollerCoasterParameters(mass,start,speed,hill,finish,80,loss)
def explore():
    mode_heading(LearningMode.EXPLORE,"Can the coaster finish?");r=simulate(controls());metric_table({"Top speed":f"{r.maximum_speed_m_s:.2f} m/s","Energy lost":f"{r.energy_lost_j:.0f} J","Track status":"Complete" if r.completed else "Stops early"});st.caption("Text outcome: "+r.outcome);animation(r,20262301);obs=st.text_input("Optional notebook observation",key="coaster_obs")
    if st.button("🎢 Run coaster",type="primary",use_container_width=True):record(ID,r.parameters.to_dict(),st.session_state.get("coaster_quiz_guess"),r.outcome,numbers(r),kidtools.process_run(ID,evaluate(r)),20262301,VERSION,obs);st.rerun()
    kidtools.mission_checklist("Roller-Coaster Energy")
def compare():
    mode_heading(LearningMode.COMPARE,"Ideal versus dissipative");a=simulate(RollerCoasterParameters(loss_per_meter_j=0));b=simulate(RollerCoasterParameters(loss_per_meter_j=150));changed_variable_banner(ChangedVariable("Dissipative loss","0 J/m","150 J/m"));metric_table({"Ideal top speed":f"{a.maximum_speed_m_s:.2f} m/s","Lossy top speed":f"{b.maximum_speed_m_s:.2f} m/s"})
    if st.button("▶ Run energy comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20262311),("Run B",b,20262312)):record(ID,r.parameters.to_dict(),"Losses reduce available mechanical energy",r.outcome,numbers(r),kidtools.process_run(ID,evaluate(r)),seed,VERSION,None,label)
    animation(b,20262312)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Energy and speed along the track");r=simulate(controls("coaster_analysis"));st.line_chart({"distance_m":r.distance_m,"potential_energy_j":r.potential_energy_j,"kinetic_energy_j":r.kinetic_energy_j,"mechanical_energy_j":r.mechanical_energy_j},x="distance_m",y=["potential_energy_j","kinetic_energy_j","mechanical_energy_j"]);st.caption("Accessible chart: potential and kinetic energy trade as height changes; total mechanical energy is constant only without losses.");st.line_chart({"distance_m":r.distance_m,"speed_m_s":r.speed_m_s},x="distance_m",y="speed_m_s");st.caption("Accessible chart: speed rises on descents and falls while climbing.")
def model():
    mode_heading(LearningMode.MODEL,"Energy determines reachable track");st.latex(r"E=mgh+\frac12mv^2\qquad E(x)=E_0-Lx");st.markdown("A track point is physically unreachable when the energy remaining after losses is less than its gravitational potential energy.");assumptions_panel((ModelAssumption("particle","Car represented as a point mass"),ModelAssumption("loss","Optional loss is constant per meter")),("No wheel rotation.","No aerodynamic speed dependence.","Track curvature does not add losses."))
def render():
    st.header("🎢 Roller-Coaster Energy");revealed=kidtools.prediction_quiz(key="coaster_quiz",question="As a coaster rolls downhill without losses, what happens to its gravitational potential energy?",options=["It becomes kinetic energy","It disappears","It stays unchanged"],correct_index=0,reveal_text="Potential energy decreases while kinetic energy and speed increase.",mission_id="coaster_predict")
    if not revealed:return
    mode=mode_navigation(key="coaster_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
