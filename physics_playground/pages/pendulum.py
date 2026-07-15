"""Four-mode Swing Machine page."""
from __future__ import annotations
import matplotlib.pyplot as plt
import streamlit as st
from physics_playground.canvas import legacy as canvas_kit
from physics_playground.canvas.pendulum import PLAYER_HEIGHT,build_pendulum_canvas,build_pendulum_comparison_canvas
from physics_playground.missions import legacy as kidtools
from physics_playground.missions.pendulum import evaluate_pendulum_missions
from physics_playground.models.pendulum import PendulumModel,PendulumParameters,PendulumResult,simulate_pendulum
from physics_playground.simulation_cache import cached_pendulum as simulate_pendulum
from physics_playground.presentation.learning_modes import ChangedVariable,LearningMode,assumptions_panel,changed_variable_banner,comparison_metrics,mode_heading,mode_navigation
from physics_playground.presentation.notebook_ui import REUSE_REQUEST_KEY,add_trial
from physics_playground.presentation.pendulum_charts import error_figure,plot_figure
from physics_playground.validation import PhysicsValidationError
from physics_playground.presentation.accessibility import render_chart
WORLDS={"Earth 🌍":9.81,"The Moon 🌕":1.62,"Jupiter 🟠":24.8};VERSION="pendulum-2.0"
def _init():
    for k,v in (("pend_nonce",0),("pend_launched",None),("pend_compare_nonce",0),("pend_compare_signature",None)):st.session_state.setdefault(k,v)
def _summary(r):
    c=st.columns(3);c[0].metric("Period",f"{r.period_s:.2f} s");c[1].metric("Top speed",f"{r.maximum_speed_m_s:.2f} m/s");c[2].metric("Energy drift",f"{r.energy_drift_fraction*100:.4f}%")
    st.caption(f"Text outcome: this {r.parameters.model.value.lower()} swing has a {r.period_s:.2f}-second period and reaches {r.maximum_speed_m_s:.2f} meters per second.")
def _metrics(r):return {"period_s":r.period_s,"maximum_speed_m_s":r.maximum_speed_m_s,"energy_drift_percent":r.energy_drift_fraction*100}
def _record(r,seed,obs,label=None,badges=()):add_trial(simulation_id="pendulum",parameters=r.parameters.to_dict(),prediction=st.session_state.get("pend_quiz_guess"),result_summary=f"{r.parameters.model.value}: period {r.period_s:.2f} s",metrics=_metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def _award(r):
    return kidtools.process_run("pendulum",evaluate_pendulum_missions(r))
def _reuse():
    q=st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id")!="pendulum":return
    p=q["parameters"];st.session_state["pend_length"]=float(p["length_m"]);st.session_state["pend_angle"]=int(round(float(p["release_angle_deg"])));st.session_state["pend_model"]=p["model"]
    st.session_state["pend_world"]=min(WORLDS,key=lambda x:abs(WORLDS[x]-float(p["gravity_m_s2"])));st.session_state["pend_learning_mode"]="Explore";del st.session_state[REUSE_REQUEST_KEY]
def render_explore():
    mode_heading(LearningMode.EXPLORE,"Choose a rope, world, and model");c1,c2=st.columns(2)
    with c1:length=st.slider("Rope length (m)",.2,10.0,2.0,.1,key="pend_length");angle=st.slider("Release angle (degrees)",5,85,30,1,key="pend_angle")
    with c2:world=st.radio("World",list(WORLDS),key="pend_world");model=PendulumModel(st.radio("Physics model",[m.value for m in PendulumModel],key="pend_model"))
    r=simulate_pendulum(PendulumParameters(length,WORLDS[world],angle,model));_summary(r);autoplay=st.session_state.pend_launched==r.parameters.to_dict()
    canvas_kit.show(build_pendulum_canvas(r,seed=20261500+st.session_state.pend_nonce,autoplay=autoplay),height=PLAYER_HEIGHT)
    obs=st.text_input("Optional notebook observation",key="pend_observation")
    if st.button("🎢 SWING!",type="primary",use_container_width=True):
        st.session_state.pend_nonce+=1;st.session_state.pend_launched=r.parameters.to_dict();badges=_award(r);_record(r,20261500+st.session_state.pend_nonce,obs,badges=badges);st.rerun()
    kidtools.mission_checklist("The Swing Machine")
def _pair(kind):
    if kind=="Short versus long pendulum":a=PendulumParameters(1,9.81,30);b=PendulumParameters(5,9.81,30);change=ChangedVariable("Length","1 m","5 m");labels=("Short","Long")
    elif kind=="Earth versus Moon":a=PendulumParameters(2,9.81,30);b=PendulumParameters(2,1.62,30);change=ChangedVariable("Gravity","Earth","Moon");labels=("Earth","Moon")
    elif kind=="Small versus large release angle":a=PendulumParameters(2,9.81,10,PendulumModel.NONLINEAR);b=PendulumParameters(2,9.81,75,PendulumModel.NONLINEAR);change=ChangedVariable("Release angle","10°","75°");labels=("Small angle","Large angle")
    else:a=PendulumParameters(2,9.81,70,PendulumModel.SMALL_ANGLE);b=PendulumParameters(2,9.81,70,PendulumModel.NONLINEAR);change=ChangedVariable("Model","Small-angle","Nonlinear");labels=("Approximation","Nonlinear")
    return simulate_pendulum(a),simulate_pendulum(b),labels,change
def render_compare():
    mode_heading(LearningMode.COMPARE,"Overlay pendulum trials");kind=st.selectbox("Comparison",["Short versus long pendulum","Earth versus Moon","Small versus large release angle","Small-angle versus nonlinear model"])
    a,b,labels,change=_pair(kind);changed_variable_banner(change);sig={"kind":kind};obs=st.text_input("Optional comparison observation",key="pend_compare_observation")
    if st.button("▶ Run comparison",type="primary",use_container_width=True):
        st.session_state.pend_compare_nonce+=1;st.session_state.pend_compare_signature=sig;n=st.session_state.pend_compare_nonce;_record(a,20261600+n,obs,"Run A");_record(b,20261700+n,obs,"Run B")
    canvas_kit.show(build_pendulum_comparison_canvas(a,b,labels=labels,seed=20261800+st.session_state.pend_compare_nonce,autoplay=st.session_state.pend_compare_signature==sig),height=PLAYER_HEIGHT)
    comparison_metrics({k:(k,v) for k,v in _metrics(a).items()},{k:(k,v) for k,v in _metrics(b).items()})
def _latest():
    if not st.session_state.pend_launched:return PendulumParameters(2,9.81,30,PendulumModel.NONLINEAR)
    d=dict(st.session_state.pend_launched);d["model"]=PendulumModel(d["model"]);return PendulumParameters(**d)
def render_analyze():
    mode_heading(LearningMode.ANALYZE,"Inspect angle, energy, and phase space");p=_latest();r=simulate_pendulum(p);_summary(r)
    for plot in r.plots:fig=plot_figure(plot);render_chart(fig,f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.");plt.close(fig)
    fig=error_figure(p.length_m,p.gravity_m_s2);render_chart(fig,"Approximation error increases as release angle grows.");plt.close(fig)
def render_model():
    mode_heading(LearningMode.MODEL,"Approximation versus nonlinear motion");st.latex(r"\ddot\theta+\frac{g}{L}\sin\theta=0");st.latex(r"\sin\theta\approx\theta\Rightarrow T_0=2\pi\sqrt{L/g}")
    st.markdown("The small-angle model is analytical. The nonlinear equation is integrated with RK4; its period grows with release angle.")
    assumptions=simulate_pendulum(PendulumParameters(2,9.81,30)).assumptions;assumptions_panel(assumptions,("Air drag and pivot friction are omitted.","The bob has no physical size or rotation.","The support and local gravity remain fixed.","The large-angle period display uses a truncated series."))
    with st.expander("🔧 Optional advanced controls"):
        length=st.number_input("Advanced length",.1,20.0,2.0);gravity=st.number_input("Advanced gravity",.1,30.0,9.81);angle=st.number_input("Advanced angle",1.0,170.0,60.0);model=PendulumModel(st.selectbox("Advanced model",[m.value for m in PendulumModel]));_summary(simulate_pendulum(PendulumParameters(length,gravity,angle,model)))
def render():
    _init();_reuse();st.header("🎢 The Swing Machine");st.markdown("Explore how length, gravity, angle, and model choice change a pendulum.")
    revealed=kidtools.prediction_quiz(key="pend_quiz",question="If you pull a small-angle swing farther, one full swing takes...",options=["More time","Less time","Almost exactly the same time"],correct_index=2,reveal_text="For small angles, period depends on length and gravity, not amplitude.",mission_id="pend_predict")
    if not revealed:st.caption("🔬 Make your prediction before results are shown.");return
    mode=mode_navigation(key="pend_learning_mode");st.divider()
    try:{LearningMode.EXPLORE:render_explore,LearningMode.COMPARE:render_compare,LearningMode.ANALYZE:render_analyze,LearningMode.MODEL:render_model}[mode]()
    except PhysicsValidationError as e:st.error(f"That setup can't run yet: {e}")
