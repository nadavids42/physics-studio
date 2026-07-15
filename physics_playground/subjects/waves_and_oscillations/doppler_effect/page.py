import streamlit as st
from physics_playground.canvas import legacy
from physics_playground.canvas.wavefronts import build_wavefront_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.presentation.notebook_ui import add_trial
from .physics import DopplerParameters,simulate
from .missions import evaluate
ID="doppler_effect";VERSION="doppler-1.0"
def values(r):return {"source_frequency_hz":r.parameters.source_frequency_hz,"observed_frequency_hz":r.observed_frequency_hz,"frequency_shift_hz":r.frequency_shift_hz,"frequency_ratio":r.frequency_ratio,"wavelength_ahead_m":r.wavelength_ahead_m,"wavelength_behind_m":r.wavelength_behind_m}
def record(r,seed,obs,label=None,badges=()):add_trial(simulation_id=ID,parameters=r.parameters.to_dict(),prediction=st.session_state.get("doppler_quiz_guess"),result_summary=r.outcome,metrics=values(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def animation(r,seed):
    frames=[{"source":f.source_position_m,"observer":f.observer_position_m,"centers":f.centers_m,"radii":f.radii_m} for f in r.frames];extent=r.parameters.speed_of_sound_m_s*r.parameters.duration_s;legacy.show(build_wavefront_document(frames=frames,world_min=min(-extent,r.parameters.initial_source_position_m-10),world_max=max(r.parameters.initial_observer_position_m+extent,r.parameters.initial_observer_position_m+10),duration_s=r.parameters.duration_s,message=r.outcome,seed=seed),height=420)
def controls(prefix="doppler"):
    c1,c2=st.columns(2)
    with c1:f=st.slider("Source frequency (Hz)",50.,1200.,440.,10.,key=f"{prefix}_f");c=st.slider("Speed of sound (m/s)",250.,400.,343.,1.,key=f"{prefix}_c")
    with c2:vs=st.slider("Source velocity (m/s; right is positive)",-200.,200.,30.,5.,key=f"{prefix}_vs");vo=st.slider("Observer velocity (m/s; right is positive)",-200.,200.,0.,5.,key=f"{prefix}_vo")
    return DopplerParameters(f,c,vs,vo)
def explore():
    mode_heading(LearningMode.EXPLORE,"Move the source and listener");r=simulate(controls());cols=st.columns(3);cols[0].metric("Emitted frequency",f"{r.parameters.source_frequency_hz:.1f} Hz");cols[1].metric("Observed frequency",f"{r.observed_frequency_hz:.1f} Hz",f"{r.frequency_shift_hz:+.1f} Hz");cols[2].metric("Motion",r.motion.value);st.caption("Text outcome: "+r.outcome);animation(r,20262601);obs=st.text_input("Optional notebook observation",key="doppler_obs")
    if st.button("🔊 Run sound experiment",type="primary",use_container_width=True):record(r,20262601,obs,badges=kidtools.process_run(ID,evaluate(r)));st.rerun()
    kidtools.mission_checklist("Sound and Doppler Effect")
def compare():
    mode_heading(LearningMode.COMPARE,"Approaching versus receding");a=simulate(DopplerParameters(source_velocity_m_s=60));b=simulate(DopplerParameters(source_velocity_m_s=-60));changed_variable_banner(ChangedVariable("Source direction","Approaching at 60 m/s","Receding at 60 m/s"));c=st.columns(2);c[0].metric("Approaching",f"{a.observed_frequency_hz:.1f} Hz");c[1].metric("Receding",f"{b.observed_frequency_hz:.1f} Hz")
    if st.button("▶ Run Doppler comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20262611),("Run B",b,20262612)):record(r,seed,"Approach raises pitch; recession lowers it",label,kidtools.process_run(ID,evaluate(r,True)))
    animation(b,20262612)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Frequency versus motion");f=st.slider("Analysis source frequency (Hz)",100.,1000.,440.,10.);c=st.slider("Analysis sound speed (m/s)",250.,400.,343.,1.);velocities=list(range(-200,201,10));source=[simulate(DopplerParameters(f,c,v,0)).observed_frequency_hz for v in velocities];observer=[simulate(DopplerParameters(f,c,0,v)).observed_frequency_hz for v in velocities];st.line_chart({"velocity_m_s":velocities,"moving_source_hz":source,"moving_observer_hz":observer},x="velocity_m_s",y=["moving_source_hz","moving_observer_hz"]);st.caption("Accessible chart: positive source velocity approaches the observer and raises frequency; positive observer velocity recedes and lowers it. The curves differ because source motion changes wavelength while observer motion changes encounter rate.")
def model():
    mode_heading(LearningMode.MODEL,"The classical Doppler equation");st.latex(r"f_{obs}=f_s\frac{c-v_o}{c-v_s}");st.markdown("Positions increase to the right, with the observer initially right of the source. Positive source velocity approaches the observer; positive observer velocity moves away. The wavelength ahead of the source is $(c-v_s)/f_s$.");assumptions_panel((ModelAssumption("medium","Sound travels through a stationary uniform medium"),ModelAssumption("subsonic","Source and observer remain subsonic")),("No wind or temperature gradients.","No reflected sound or finite source size.","Relativistic effects are not applicable to this sound model."))
def render():
    st.header("🔊 Sound and Doppler Effect");revealed=kidtools.prediction_quiz(key="doppler_quiz",question="An ambulance approaches you while its siren emits a steady frequency. What pitch do you hear?",options=["Higher","Lower","Unchanged"],correct_index=0,reveal_text="Approaching wavefronts are compressed, so they arrive more frequently.",mission_id="doppler_predict")
    if not revealed:return
    mode=mode_navigation(key="doppler_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
