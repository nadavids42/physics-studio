"""Four-mode Double Pendulum of Chaos page."""
from __future__ import annotations
import matplotlib.pyplot as plt
import streamlit as st
from physics_playground.canvas import legacy as canvas_kit
from physics_playground.canvas.double_pendulum import PLAYER_HEIGHT,build_double_canvas
from physics_playground.missions import legacy as kidtools
from physics_playground.missions.double_pendulum import evaluate_double_missions
from physics_playground.models.double_pendulum import DoublePendulumParameters,DoublePendulumResult,convergence_warning,simulate_double_pendulum
from physics_playground.simulation_cache import cached_double_pendulum as simulate_double_pendulum
from physics_playground.presentation.double_pendulum_charts import plot_figure
from physics_playground.presentation.learning_modes import ChangedVariable,LearningMode,assumptions_panel,changed_variable_banner,comparison_metrics,mode_heading,mode_navigation
from physics_playground.presentation.notebook_ui import REUSE_REQUEST_KEY,add_trial
from physics_playground.validation import PhysicsValidationError
from physics_playground.presentation.accessibility import render_chart
VERSION="double-pendulum-rk4-2.0"
def _init():
    for k,v in (("chaos_nonce",0),("chaos_launched",None),("chaos_compare_nonce",0),("chaos_compare_signature",None)):st.session_state.setdefault(k,v)
def _summary(r):
    c=st.columns(4);c[0].metric("Energy drift",f"{r.energy_drift_fraction*100:.4f}%");c[1].metric("Angular separation",f"{r.final_angular_separation_rad:.3f} rad");c[2].metric("Cartesian separation",f"{r.final_cartesian_separation_m:.3f} m");c[3].metric("Divergence rate",f"{r.divergence_rate_per_s:.3f} 1/s" if r.divergence_rate_per_s is not None else "n/a")
    st.caption(f"Text outcome: the paired pendulums finish {r.final_cartesian_separation_m:.3f} meters apart with angular separation {r.final_angular_separation_rad:.3f} radians.")
def _metrics(r):return {"energy_drift_percent":r.energy_drift_fraction*100,"angular_separation_rad":r.final_angular_separation_rad,"cartesian_separation_m":r.final_cartesian_separation_m,"divergence_rate_per_s":r.divergence_rate_per_s or 0}
def _record(r,seed,obs,label=None,badges=()):add_trial(simulation_id="double_pendulum",parameters=r.parameters.to_dict(),prediction=st.session_state.get("chaos_quiz_guess"),result_summary=f"Final separation {r.final_cartesian_separation_m:.3f} m",metrics=_metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def _award(r):
    return kidtools.process_run("double_pendulum",evaluate_double_missions(r))
def _reuse():
    q=st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id")!="double_pendulum":return
    p=q["parameters"]
    for key,name in (("chaos_angle1","angle_1_deg"),("chaos_angle2","angle_2_deg"),("chaos_perturb","perturbation_deg"),("chaos_dt","time_step_s")):st.session_state[key]=float(p[name])
    st.session_state["chaos_learning_mode"]="Explore";del st.session_state[REUSE_REQUEST_KEY]
def render_explore():
    mode_heading(LearningMode.EXPLORE,"Release two almost-identical systems");c1,c2=st.columns(2)
    with c1:a1=st.slider("First arm angle",-170.0,170.0,110.0,1.0,key="chaos_angle1");a2=st.slider("Second arm angle",-170.0,170.0,-20.0,1.0,key="chaos_angle2")
    with c2:perturb=st.number_input("Perturbation size (degrees)",0.0,10.0,.1,.01,key="chaos_perturb");dt=st.number_input("Integration time step",.001,.05,.005,.001,key="chaos_dt")
    p=DoublePendulumParameters(angle_1_deg=a1,angle_2_deg=a2,perturbation_deg=perturb,time_step_s=dt);warning=convergence_warning(p)
    if warning:st.warning(warning)
    r=simulate_double_pendulum(p);_summary(r);show_separation=st.checkbox("Show recorded separation callout",value=True,key="chaos_show_separation");inspect=st.selectbox("Optional visual inspection focus",["Fixed camera (both systems)","Baseline A","Perturbed B"],key="chaos_inspect");inspect_system={"Baseline A":"a","Perturbed B":"b"}.get(inspect);autoplay=st.session_state.chaos_launched==p.to_dict();canvas_kit.show(build_double_canvas(r,seed=20262600+st.session_state.chaos_nonce,autoplay=autoplay,show_separation=show_separation,inspect_system=inspect_system),height=PLAYER_HEIGHT)
    obs=st.text_input("Optional notebook observation",key="chaos_observation")
    if st.button("🌀 RELEASE!",type="primary",use_container_width=True):st.session_state.chaos_nonce+=1;st.session_state.chaos_launched=p.to_dict();badges=_award(r);_record(r,20262600+st.session_state.chaos_nonce,obs,badges=badges);st.rerun()
    kidtools.mission_checklist("Double Pendulum of Chaos")
def _pair(kind):
    if kind=="Different perturbation sizes":a=DoublePendulumParameters(perturbation_deg=.01);b=DoublePendulumParameters(perturbation_deg=1);change=ChangedVariable("Perturbation","0.01°","1°")
    elif kind=="Different initial angles":a=DoublePendulumParameters(angle_1_deg=90);b=DoublePendulumParameters(angle_1_deg=130);change=ChangedVariable("Initial angle 1","90°","130°")
    elif kind=="Different mass ratios":a=DoublePendulumParameters(mass_1_kg=1,mass_2_kg=.3);b=DoublePendulumParameters(mass_1_kg=1,mass_2_kg=3);change=ChangedVariable("Mass ratio m₂/m₁","0.3","3")
    else:a=DoublePendulumParameters(time_step_s=.002);b=DoublePendulumParameters(time_step_s=.02);change=ChangedVariable("Time step","0.002","0.020")
    return simulate_double_pendulum(a),simulate_double_pendulum(b),change
def render_compare():
    mode_heading(LearningMode.COMPARE,"Compare chaos experiments");kind=st.selectbox("Comparison",["Different perturbation sizes","Different initial angles","Different mass ratios","Different integration time steps"]);a,b,change=_pair(kind);changed_variable_banner(change);sig={"kind":kind};obs=st.text_input("Optional comparison observation",key="chaos_compare_observation")
    if st.button("▶ Run comparison",type="primary",use_container_width=True):st.session_state.chaos_compare_nonce+=1;st.session_state.chaos_compare_signature=sig;n=st.session_state.chaos_compare_nonce;_record(a,20262700+n,obs,"Run A");_record(b,20262800+n,obs,"Run B")
    st.markdown("#### Run A");canvas_kit.show(build_double_canvas(a,seed=20262900+st.session_state.chaos_compare_nonce,autoplay=st.session_state.chaos_compare_signature==sig),height=PLAYER_HEIGHT)
    st.markdown("#### Run B");canvas_kit.show(build_double_canvas(b,seed=20263000+st.session_state.chaos_compare_nonce,autoplay=st.session_state.chaos_compare_signature==sig),height=PLAYER_HEIGHT)
    comparison_metrics({k:(k,v) for k,v in _metrics(a).items()},{k:(k,v) for k,v in _metrics(b).items()})
def _latest():return DoublePendulumParameters(**st.session_state.chaos_launched) if st.session_state.chaos_launched else DoublePendulumParameters()
def render_analyze():
    mode_heading(LearningMode.ANALYZE,"Measure divergence and convergence");r=simulate_double_pendulum(_latest());_summary(r)
    for plot in r.plots:fig=plot_figure(plot);render_chart(fig,f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.");plt.close(fig)
def render_model():
    mode_heading(LearningMode.MODEL,"Coupled nonlinear equations and sensitivity");st.markdown("The two coupled second-order equations are integrated as four first-order equations with RK4. Tiny initial differences grow because the nonlinear flow stretches nearby trajectories through phase space.")
    st.latex(r"\Delta(t)\approx\Delta_0e^{\lambda t}\quad\Rightarrow\quad\ln\Delta(t)\approx\ln\Delta_0+\lambda t")
    assumptions=simulate_double_pendulum(DoublePendulumParameters(duration_s=2)).assumptions;assumptions_panel(assumptions,("Rods cannot bend or collide.","Air resistance and pivot friction are omitted.","The fitted divergence rate is finite-time and only approximate.","Chaos makes long-term trajectories timestep-sensitive even when conserved quantities look good."))
def render():
    _init();_reuse();st.header("🌀 Double Pendulum of Chaos");st.markdown("Release two nearly identical double pendulums and watch predictability disappear.")
    revealed=kidtools.prediction_quiz(key="chaos_quiz",question="Two double pendulums start almost—but not exactly—the same. What happens?",options=["They remain nearly identical","They can separate dramatically","They become perfectly synchronized"],correct_index=1,reveal_text="Nonlinear dynamics can amplify a microscopic difference into completely different motion.",mission_id="chaos_predict")
    if not revealed:st.caption("🔬 Make your prediction before results are shown.");return
    mode=mode_navigation(key="chaos_learning_mode");st.divider()
    try:{LearningMode.EXPLORE:render_explore,LearningMode.COMPARE:render_compare,LearningMode.ANALYZE:render_analyze,LearningMode.MODEL:render_model}[mode]()
    except PhysicsValidationError as e:st.error(f"That setup can't run yet: {e}")
