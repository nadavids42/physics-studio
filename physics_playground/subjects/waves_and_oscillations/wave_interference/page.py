import math
import matplotlib.pyplot as plt
import streamlit as st
from physics_playground.canvas import legacy
from physics_playground.canvas.scalar_field import build_scalar_field_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.presentation.chart_system import series_figure
from physics_playground.presentation.accessibility import render_chart
from .physics import WaveSource,WaveInterferenceParameters,simulate
from .missions import evaluate
ID="wave_interference";VERSION="wave-interference-1.0"
def metrics(r):return {"peak_displacement":max(abs(r.maximum_amplitude),abs(r.minimum_amplitude)),"maximum_displacement":r.maximum_amplitude,"minimum_displacement":r.minimum_amplitude,"center_rms":r.measurements[2].rms_displacement,"source_count":float(len(r.parameters.sources))}
def record(r,seed,observation,label=None,badges=()):add_trial(simulation_id=ID,parameters=r.parameters.to_dict(),prediction=st.session_state.get("wave_quiz_guess"),result_summary=r.outcome,metrics=metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=observation,label=label)
def animation(r,seed,autoplay=False):
    phases=[math.degrees(source.phase_rad)%360 for source in r.parameters.sources];phase_delta=(phases[1]-phases[0])%360 if len(phases)>1 else 0;kind="Constructive interference" if min(phase_delta,360-phase_delta)<15 else ("Destructive interference" if abs(phase_delta-180)<15 else "Mixed interference")
    legacy.show(build_scalar_field_document(x=r.position_m,frames=r.superposition_frames,source_frames=r.source_frames,sources=tuple({"amplitude":source.amplitude,"phaseDeg":phase} for source,phase in zip(r.parameters.sources,phases)),measurements=tuple({"index":min(range(len(r.position_m)),key=lambda i:abs(r.position_m[i]-m.position_m))} for m in r.measurements),time_s=r.time_s,interference_label=f"{kind}\nΔφ = {phase_delta:.0f}°",duration_s=r.parameters.duration_s,accessible_label="Scientific graph of source waves and their exact pointwise resultant. "+r.outcome,completion_message=r.outcome,seed=seed,autoplay=autoplay),height=460)
def controls(prefix="wave"):
    count=st.slider("Number of wave sources",2,4,2,key=f"{prefix}_count");speed=st.slider("Propagation speed (m/s)",.5,10.,2.,.1,key=f"{prefix}_speed");sources=[]
    for i in range(count):
        with st.expander(f"Source {i+1}",expanded=i<2):
            c1,c2,c3=st.columns(3);amplitude=c1.slider("Amplitude",0.,3.,1.,.1,key=f"{prefix}_a{i}");wavelength=c2.slider("Wavelength (m)",.25,5.,2.,.05,key=f"{prefix}_l{i}");phase_deg=c3.slider("Phase (degrees)",0,360,0 if i==0 else 0,5,key=f"{prefix}_p{i}");frequency=speed/wavelength;st.caption(f"Frequency = {frequency:.2f} Hz · propagation speed = {frequency*wavelength:.2f} m/s");sources.append(WaveSource(amplitude,wavelength,frequency,math.radians(phase_deg)))
    return WaveInterferenceParameters(tuple(sources))
def explore():
    mode_heading(LearningMode.EXPLORE,"Build and combine traveling waves");r=simulate(controls());peak=max(abs(r.maximum_amplitude),abs(r.minimum_amplitude));c=st.columns(3);c[0].metric("Peak displacement",f"{peak:.2f}");c[1].metric("Center RMS",f"{r.measurements[2].rms_displacement:.2f}");c[2].metric("Sources",len(r.parameters.sources));st.caption("Text outcome: "+r.outcome);animation(r,20262501);position=st.slider("Measurement position (m)",0.,r.parameters.domain_length_m,r.parameters.domain_length_m/2,.1);time=st.slider("Measurement time (s)",0.,r.parameters.duration_s,0.,.05);st.metric("Displacement at selected position and time",f"{r.displacement_at(position,time):.3f}");obs=st.text_input("Optional notebook observation",key="wave_obs")
    if st.button("🌊 Run waves",type="primary",use_container_width=True):record(r,20262501,obs,badges=kidtools.process_run(ID,evaluate(r)));st.rerun()
    kidtools.mission_checklist("Wave Interference")
def compare():
    mode_heading(LearningMode.COMPARE,"In phase versus opposite phase");common=WaveSource(1,2,1,0);a=simulate(WaveInterferenceParameters((common,WaveSource(1,2,1,0))));b=simulate(WaveInterferenceParameters((common,WaveSource(1,2,1,math.pi))));changed_variable_banner(ChangedVariable("Source 2 phase","0°","180°"));c=st.columns(2);c[0].metric("Run A peak",f"{metrics(a)['peak_displacement']:.2f}");c[1].metric("Run B peak",f"{metrics(b)['peak_displacement']:.2f}")
    if st.button("▶ Run phase comparison",use_container_width=True):
        for label,r,seed in (("Run A",a,20262511),("Run B",b,20262512)):record(r,seed,"Phase controls reinforcement or cancellation",label,kidtools.process_run(ID,evaluate(r,True)))
    animation(b,20262512)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Measure sources and superposition");r=simulate(controls("wave_analysis"));snapshot={f"Source {i+1}":list(frames[0]) for i,frames in enumerate(r.source_frames)};snapshot["Resultant"]=list(r.superposition_frames[0]);figure=series_figure(x=list(r.position_m),series=snapshot,x_label="Position (m)",y_label="Displacement",title="Source waves and exact resultant at t = 0 s");render_chart(figure,"Individual source displacements and their point-by-point resultant at time zero.");plt.close(figure);index=len(r.position_m)//2;center=series_figure(x=list(r.time_s),series={"Center displacement":[frame[index] for frame in r.superposition_frames]},x_label="Time (s)",y_label="Displacement",title="Resultant displacement at the center");render_chart(center,"Summed displacement over time at the center measurement point.");plt.close(center);st.markdown("| Position | Minimum | Maximum | RMS |\n|---:|---:|---:|---:|\n"+"\n".join(f"| {m.position_m:.2f} m | {m.minimum_displacement:.3f} | {m.maximum_displacement:.3f} | {m.rms_displacement:.3f} |" for m in r.measurements))
def model():
    mode_heading(LearningMode.MODEL,"Linear superposition");st.latex(r"y_i(x,t)=A_i\sin\left[2\pi\left(\frac{x}{\lambda_i}-f_it\right)+\phi_i\right]");st.latex(r"y_{total}(x,t)=\sum_i y_i(x,t),\qquad v_i=f_i\lambda_i");st.markdown("Equal waves in phase add constructively. A 180° phase difference produces destructive interference; equal amplitudes can cancel exactly.");assumptions_panel((ModelAssumption("linear","The medium responds linearly"),ModelAssumption("traveling","Sources create ideal sinusoidal traveling waves")),("No reflection or boundary effects.","No damping or dispersion.","The display is a one-dimensional scalar field."))
def render():
    st.header("🌊 Wave Interference");revealed=kidtools.prediction_quiz(key="wave_quiz",question="Two identical waves arrive in phase. What happens to their amplitudes?",options=["They add","They cancel","Frequency doubles"],correct_index=0,reveal_text="Their displacements add point by point, producing constructive interference.",mission_id="wave_predict")
    if not revealed:return
    mode=mode_navigation(key="wave_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
