import math
import matplotlib.pyplot as plt
import streamlit as st
from physics_playground.canvas import legacy
from physics_playground.canvas.diffusion_player import build_diffusion_document
from physics_playground.contracts import ModelAssumption
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.learning_modes import LearningMode,mode_navigation,mode_heading,ChangedVariable,changed_variable_banner,assumptions_panel
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.presentation.chart_system import series_figure
from physics_playground.presentation.accessibility import render_chart
from .physics import DiffusionParameters,WalkDimension,simulate,MAX_PARTICLES,MAX_UPDATES
from .missions import evaluate
ID="diffusion";VERSION="diffusion-1.0"
def metrics(r):return {"mean_displacement_x_m":r.mean_displacement_x_m,"mean_displacement_y_m":r.mean_displacement_y_m,"mean_squared_displacement_m2":r.mean_squared_displacement_m2,"diffusion_coefficient_m2_s":r.diffusion_coefficient_m2_s,"elapsed_time_s":r.elapsed_time_s}
def record(r,obs,label=None,badges=()):add_trial(simulation_id=ID,parameters=r.parameters.to_dict(),prediction=st.session_state.get("diffusion_quiz_guess"),result_summary=r.outcome,metrics=metrics(r),earned_badges=badges,random_seed=r.parameters.seed,model_version=VERSION,learner_observation=obs,label=label)
def diagram(r):
    extent=max((abs(x) for path in r.sample_trajectories for point in path for x in point),default=1.)*1.1
    legacy.show(build_diffusion_document(paths=r.sample_trajectories,dimensions=int(r.parameters.dimensions),extent=extent,message=r.outcome,seed=r.parameters.seed,rms_distance_m=math.sqrt(r.mean_squared_displacement_m2),sampled_particle_count=r.sampled_particle_count),height=590)
def distribution_bins(values,bin_count=None):
    """Return deterministic equal-width histogram geometry in meters."""
    data=tuple(float(value) for value in values)
    if not data:return (),(),0.
    count=bin_count or max(5,min(30,math.ceil(math.sqrt(len(data)))));low=min(data);high=max(data)
    if math.isclose(low,high):low-=.5;high+=.5
    width=(high-low)/count;bins=[0]*count
    for value in data:bins[min(count-1,max(0,int((value-low)/width)))]+=1
    centers=tuple(low+(index+.5)*width for index in range(count));return centers,tuple(bins),width
def controls(prefix="diffusion"):
    c=st.columns(3);dimensions=WalkDimension(c[0].radio("Walk dimensions",[1,2],format_func=lambda x:f"{x}D",horizontal=True,key=f"{prefix}_dimensions"));particles=c[1].slider("Particle count",10,MAX_PARTICLES,500,10,key=f"{prefix}_particles");steps=c[2].slider("Number of steps",10,200,100,10,key=f"{prefix}_steps");c=st.columns(3);step=c[0].slider("Step size (m)",.01,1.,.1,.01,key=f"{prefix}_step_size");dt=c[1].slider("Timestep (s)",.001,1.,.05,.001,key=f"{prefix}_dt");seed=c[2].number_input("Random seed",value=20263401,step=1,key=f"{prefix}_seed");c=st.columns(2);bx=c[0].slider("Horizontal bias",-1.,1.,0.,.05,key=f"{prefix}_bias_x");by=c[1].slider("Vertical bias",-1.,1.,0.,.05,key=f"{prefix}_bias_y",disabled=dimensions is WalkDimension.ONE_D);updates=particles*steps;st.caption(f"Computational budget: {updates:,} of {MAX_UPDATES:,} particle updates. Only a bounded sample is sent to the browser.");return DiffusionParameters(particles,dimensions,steps,step,dt,bx,by if dimensions is WalkDimension.TWO_D else 0.,int(seed))
def summary(r):c=st.columns(3);c[0].metric("Mean x displacement",f"{r.mean_displacement_x_m:.3f} m");c[1].metric("Mean y displacement",f"{r.mean_displacement_y_m:.3f} m");c[2].metric("Mean-squared displacement",f"{r.mean_squared_displacement_m2:.3f} m²");st.caption("Text outcome: "+r.outcome)
def explore():
    mode_heading(LearningMode.EXPLORE,"Follow many unpredictable walkers");p=controls();r=simulate(p);summary(r);diagram(r);obs=st.text_input("Optional notebook observation",key="diffusion_obs")
    if st.button("🟣 Run random walks",type="primary",use_container_width=True):record(r,obs,badges=kidtools.process_run(ID,evaluate(r)));st.rerun()
    kidtools.mission_checklist("Diffusion and Random Walks")
def compare():
    mode_heading(LearningMode.COMPARE,"Unbiased versus biased motion");a=simulate(DiffusionParameters(seed=20263411));b=simulate(DiffusionParameters(bias_x=.35,seed=20263411));changed_variable_banner(ChangedVariable("Horizontal bias","0.00","0.35"));c=st.columns(2);c[0].metric("Run A mean x",f"{a.mean_displacement_x_m:.2f} m");c[1].metric("Run B mean x",f"{b.mean_displacement_x_m:.2f} m")
    if st.button("▶ Run walk comparison",use_container_width=True):
        for label,r in (("Run A",a),("Run B",b)):record(r,"Bias shifts the distribution while random spreading remains",label,kidtools.process_run(ID,evaluate(r,True)))
    diagram(b)
def analyze():
    mode_heading(LearningMode.ANALYZE,"Distributions, trajectories, and MSD growth");p=controls("diffusion_analysis");r=simulate(p);centers,counts,width=distribution_bins(r.final_x_m);histogram,axis=plt.subplots();axis.bar(centers,counts,width=width*.9,label="Final x distribution");axis.set_xlabel("Final horizontal position (m)");axis.set_ylabel("Sampled particle count");axis.set_title(f"Binned final-position distribution ({len(counts)} bins)");render_chart(histogram,"A properly binned count distribution of sampled particles' final horizontal positions, measured in meters.");plt.close(histogram);times=[p.timestep_s*k for k in range(1,p.steps+1,max(1,p.steps//100))];theory=[2*int(p.dimensions)*r.diffusion_coefficient_m2_s*t for t in times];msd=series_figure(x=times,series={"Unbiased theoretical MSD":theory},x_label="Elapsed time (s)",y_label="Mean-squared displacement (m²)",title="Theoretical diffusive spreading");render_chart(msd,"The unbiased theoretical mean-squared displacement grows linearly with elapsed time in square meters.");plt.close(msd);diagram(r)
def model():
    mode_heading(LearningMode.MODEL,"Random steps become diffusion");st.latex(r"\langle r^2\rangle=2dDt,\qquad D=\frac{\ell^2}{2d\Delta t}");st.latex(r"\langle x\rangle=N\ell b_x");assumptions_panel((ModelAssumption("independent","Particle steps are independent pseudorandom draws"),ModelAssumption("fixed","Every step has fixed length and timestep"),ModelAssumption("unbounded","No walls or particle interactions")),("This is a discrete walk, not molecular dynamics.","Bias is an imposed drift rather than a calculated force.","Finite samples fluctuate around statistical expectations."))
def render():
    st.header("🟣 Diffusion and Random Walks");revealed=kidtools.prediction_quiz(key="diffusion_quiz",question="For many unbiased walkers, what happens to the mean-squared displacement as time increases?",options=["It grows roughly linearly","It stays exactly zero","It always decreases"],correct_index=0,reveal_text="Random positive and negative steps cancel in the mean, but their squared distances accumulate.",mission_id="diffusion_predict")
    if not revealed:return
    mode=mode_navigation(key="diffusion_mode");{LearningMode.EXPLORE:explore,LearningMode.COMPARE:compare,LearningMode.ANALYZE:analyze,LearningMode.MODEL:model}[mode]()
