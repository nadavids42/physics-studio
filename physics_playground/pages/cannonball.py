"""Four-mode Cannonball Launcher page."""

from __future__ import annotations

import random
import matplotlib.pyplot as plt
import streamlit as st

from physics_playground.canvas import legacy as canvas_kit
from physics_playground.canvas.cannonball import PLAYER_HEIGHT, build_cannon_canvas, build_cannon_comparison_canvas
from physics_playground.missions import legacy as kidtools
from physics_playground.missions.cannonball import evaluate_cannonball_missions
from physics_playground.models.projectile import ProjectileParameters, ProjectileResult, simulate_no_drag, simulate_projectile
from physics_playground.simulation_cache import cached_projectile as simulate_projectile, cached_projectile_no_drag as simulate_no_drag
from physics_playground.presentation.learning_modes import ChangedVariable, LearningMode, assumptions_panel, changed_variable_banner, comparison_metrics, mode_heading, mode_navigation
from physics_playground.presentation.notebook_ui import REUSE_REQUEST_KEY, add_trial
from physics_playground.presentation.projectile_charts import plot_figure, range_by_angle_figure
from physics_playground.validation import PhysicsValidationError
from physics_playground.presentation.accessibility import render_chart

WORLDS={"Earth 🌍":9.81,"The Moon 🌕":1.62,"Jupiter 🟠":24.8}
MODEL_VERSION="projectile-2.0"


def _init() -> None:
    st.session_state.setdefault("cannon_target_seed",20260710)
    st.session_state.setdefault("cannon_launch_nonce",0)
    st.session_state.setdefault("cannon_launched_parameters",None)
    st.session_state.setdefault("cannon_compare_nonce",0)
    st.session_state.setdefault("cannon_compare_signature",None)
    st.session_state.setdefault("cannon_target_override",None)


def _target() -> float:
    if st.session_state.cannon_target_override is not None:return float(st.session_state.cannon_target_override)
    return round(random.Random(st.session_state.cannon_target_seed).uniform(15,55),1)


def _apply_reuse()->None:
    request=st.session_state.get(REUSE_REQUEST_KEY)
    if not request or request.get("simulation_id")!="cannonball":return
    p=request["parameters"]
    st.session_state["cannon_speed"]=min(40.0,max(5.0,float(p["launch_speed_m_s"])))
    st.session_state["cannon_angle"]=min(89,max(5,int(round(float(p["launch_angle_deg"])))))
    gravity=float(p["gravity_m_s2"]);st.session_state["cannon_world"]=min(WORLDS,key=lambda label:abs(WORLDS[label]-gravity))
    st.session_state["cannon_target_override"]=float(p.get("target_m",_target()))
    st.session_state["cannon_learning_mode"]=LearningMode.EXPLORE.value
    del st.session_state[REUSE_REQUEST_KEY];st.toast(f"Reused setup from Trial #{request['source_trial']}.")


def _summary(result: ProjectileResult) -> None:
    cols=st.columns(3); cols[0].metric("Range",f"{result.range_m:.1f} m"); cols[1].metric("Maximum height",f"{result.maximum_height_m:.1f} m");
    cols[2].metric("Flight time",f"{result.flight_time_s:.2f} s" if result.landed else "Did not land")
    st.caption(f"Text outcome: the projectile {'landed' if result.landed else 'did not land'} after traveling {result.range_m:.1f} meters horizontally and reaching {result.maximum_height_m:.1f} meters high.")


def _message(result: ProjectileResult,target:float)->str:
    if not result.landed:return "The simulation limit was reached before the cannonball landed."
    miss=result.range_m-target
    return (f"🎯 BULLSEYE! Landed at {result.range_m:.1f} m." if abs(miss)<=2 else
            f"Missed by {abs(miss):.1f} m ({'long' if miss>0 else 'short'}).")


def _metrics(result:ProjectileResult)->dict[str,float]:
    return {"range_m":result.range_m,"maximum_height_m":result.maximum_height_m,"flight_time_s":result.flight_time_s,
            "impact_speed_m_s":result.impact_speed_m_s or 0.0,"energy_lost_j":result.metric("energy_lost").value}


def _record(result:ProjectileResult,target:float,seed:int,observation:str|None,label:str|None=None,badges:tuple[str,...]=())->None:
    add_trial(simulation_id="cannonball",parameters={**result.parameters.to_dict(),"target_m":target},
              prediction=st.session_state.get("cannon_quiz_guess"),result_summary=_message(result,target),metrics=_metrics(result),
              earned_badges=badges,random_seed=seed,model_version=MODEL_VERSION,learner_observation=observation,label=label)


def _award(result:ProjectileResult,target:float)->tuple[str,...]:
    return kidtools.process_run("cannonball",evaluate_cannonball_missions(result,target))


def render_explore()->None:
    mode_heading(LearningMode.EXPLORE,"Aim, predict, and fire")
    c1,c2=st.columns(2)
    with c1:speed=st.slider("Launch speed (m/s)",5.0,40.0,20.0,.5,key="cannon_speed")
    with c2:angle=st.slider("Launch angle (degrees)",5,89,45,1,key="cannon_angle")
    world=st.radio("World",list(WORLDS),horizontal=True,key="cannon_world"); gravity=WORLDS[world]
    same=st.checkbox("Reuse the same target",value=True,key="cannon_reuse_target")
    if st.button("🔄 New deterministic target",disabled=same):
        st.session_state.cannon_target_override=None;st.session_state.cannon_target_seed+=1;st.rerun()
    target=_target();st.info(f"🎯 Target: {target:.1f} m")
    result=simulate_no_drag(ProjectileParameters(speed,angle,gravity))
    _summary(result)
    autoplay=st.session_state.cannon_launched_parameters==result.parameters.to_dict()
    doc=build_cannon_canvas(result,target_m=target,message=_message(result,target),seed=st.session_state.cannon_target_seed,autoplay=autoplay)
    canvas_kit.show(doc,height=PLAYER_HEIGHT)
    observation=st.text_input("Optional notebook observation",placeholder="What did you notice?",key="cannon_observation")
    if st.button("💥 FIRE!",type="primary",use_container_width=True):
        nonce=st.session_state.cannon_launch_nonce+1;st.session_state.cannon_launch_nonce=nonce
        st.session_state.cannon_launched_parameters=result.parameters.to_dict();badges=_award(result,target)
        _record(result,target,st.session_state.cannon_target_seed,observation,badges=badges)
        if not same:st.session_state.cannon_target_override=None;st.session_state.cannon_target_seed+=1
        st.rerun()
    kidtools.mission_checklist("Cannonball Launcher")


def _comparison_results(kind:str)->tuple[ProjectileResult,ProjectileResult,tuple[str,str],ChangedVariable]:
    if kind=="30° versus 60°":
        a=simulate_no_drag(ProjectileParameters(25,30,9.81));b=simulate_no_drag(ProjectileParameters(25,60,9.81));
        return a,b,("30°","60°"),ChangedVariable("Launch angle","30°","60°")
    if kind=="With drag versus without drag":
        a=simulate_no_drag(ProjectileParameters(25,40,9.81));b=simulate_projectile(ProjectileParameters(25,40,9.81,drag_coefficient_kg_m=.05));
        return a,b,("No drag","Quadratic drag"),ChangedVariable("Air resistance","None","Quadratic drag")
    a=simulate_no_drag(ProjectileParameters(25,45,9.81));b=simulate_no_drag(ProjectileParameters(25,45,1.62));
    return a,b,("Earth","Moon"),ChangedVariable("Gravity","9.81 m/s²","1.62 m/s²")


def render_compare()->None:
    mode_heading(LearningMode.COMPARE,"Overlay two trajectories")
    kind=st.selectbox("Comparison",["30° versus 60°","With drag versus without drag","Earth versus Moon"])
    a,b,labels,change=_comparison_results(kind);changed_variable_banner(change);target=_target()
    signature={"kind":kind,"seed":st.session_state.cannon_target_seed}
    observation=st.text_input("Optional comparison observation",key="cannon_compare_observation")
    if st.button("▶ Run comparison",type="primary",use_container_width=True):
        st.session_state.cannon_compare_nonce+=1;st.session_state.cannon_compare_signature=signature
        nonce=st.session_state.cannon_compare_nonce;_record(a,target,20260800+nonce,observation,"Run A");_record(b,target,20260900+nonce,observation,"Run B")
    doc=build_cannon_comparison_canvas(a,b,target_m=target,labels=labels,seed=20261000+st.session_state.cannon_compare_nonce,
                                       autoplay=st.session_state.cannon_compare_signature==signature)
    canvas_kit.show(doc,height=PLAYER_HEIGHT)
    comparison_metrics({k:(k,v) for k,v in _metrics(a).items()},{k:(k,v) for k,v in _metrics(b).items()})


def _latest()->ProjectileParameters:
    saved=st.session_state.get("cannon_launched_parameters")
    return ProjectileParameters(**saved) if saved else ProjectileParameters(25,40,9.81)


def render_analyze()->None:
    mode_heading(LearningMode.ANALYZE,"Inspect the flight data")
    base=_latest();drag=st.slider("Analysis drag coefficient",0.0,.3,base.drag_coefficient_kg_m,.01)
    result=simulate_projectile(ProjectileParameters(base.launch_speed_m_s,base.launch_angle_deg,base.gravity_m_s2,
        base.initial_height_m,base.mass_kg,drag,base.time_step_s,base.max_time_s,base.samples))
    if not result.landed:st.warning(result.warnings[0])
    _summary(result)
    for plot in result.plots:fig=plot_figure(plot);render_chart(fig,f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.");plt.close(fig)
    fig=range_by_angle_figure(result.parameters.launch_speed_m_s,result.parameters.gravity_m_s2);render_chart(fig,"Range rises toward 45 degrees and then falls symmetrically.");plt.close(fig)


def render_model()->None:
    mode_heading(LearningMode.MODEL,"Equations, assumptions, and numerical methods")
    st.markdown("#### No-drag analytic model");st.latex(r"x(t)=v_0\cos(\theta)t")
    st.latex(r"y(t)=y_0+v_0\sin(\theta)t-\frac12gt^2")
    st.latex(r"R=\frac{v_0^2\sin(2\theta)}{g}\quad(y_0=0)")
    st.markdown("#### Quadratic-drag numerical model");st.latex(r"\vec F_d=-k|\vec v|\vec v")
    st.markdown("The drag model uses fixed-step fourth-order Runge–Kutta (RK4). When a step crosses the ground, the final state and time are linearly interpolated to **exactly y = 0**, avoiding range overshoot from simple clamping.")
    assumptions=simulate_no_drag(ProjectileParameters(20,45)).assumptions
    assumptions_panel(assumptions,("Earth curvature and rotation are ignored.","Wind, lift, spin, and changing air density are omitted.",
        "The drag coefficient combines shape, area, and air density into one constant.","Fixed-step RK4 is accurate but not adaptive."))
    with st.expander("🔧 Optional advanced controls"):
        c1,c2,c3=st.columns(3)
        with c1:speed=st.number_input("Model speed",1.0,100.0,25.0);angle=st.number_input("Model angle",1.0,89.0,40.0)
        with c2:mass=st.number_input("Mass (kg)",.1,50.0,5.0);drag=st.number_input("Drag k",0.0,2.0,.05,.01)
        with c3:dt=st.number_input("Time step (s)",.0005,.1,.005,.0005,format="%.4f");limit=st.number_input("Maximum time (s)",1.0,300.0,120.0)
        result=simulate_projectile(ProjectileParameters(speed,angle,9.81,mass_kg=mass,drag_coefficient_kg_m=drag,time_step_s=dt,max_time_s=limit))
        _summary(result)
        if not result.landed:st.error("The projectile did not land before the maximum-time limit. Increase the limit or inspect the setup.")


def render()->None:
    _init();_apply_reuse();st.header("🎯 Cannonball Launcher")
    st.markdown("Launch a cannonball, compare trajectories, analyze the measurements, or inspect the model.")
    revealed=kidtools.prediction_quiz(key="cannon_quiz",question="For maximum no-drag range on level ground, which angle wins?",
        options=["15°","45°","75°","90°"],correct_index=1,
        reveal_text="**45 degrees** balances horizontal speed and time aloft.",mission_id="cannon_predict")
    if not revealed:st.caption("🔬 Make your prediction before any results are shown.");return
    mode=mode_navigation(key="cannon_learning_mode");st.divider()
    try:
        {LearningMode.EXPLORE:render_explore,LearningMode.COMPARE:render_compare,LearningMode.ANALYZE:render_analyze,LearningMode.MODEL:render_model}[mode]()
    except PhysicsValidationError as error:st.error(f"That setup can't run yet: {error}")
