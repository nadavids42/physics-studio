"""Four-mode Big Fall page."""
from __future__ import annotations
import matplotlib.pyplot as plt
import streamlit as st
from physics_playground.canvas import legacy as canvas_kit
from physics_playground.canvas.earth_tunnel import PLAYER_HEIGHT,build_tunnel_canvas,build_tunnel_comparison_canvas
from physics_playground.missions import legacy as kidtools
from physics_playground.missions.earth_tunnel import evaluate_tunnel_missions
from physics_playground.models.earth_tunnel import TunnelModel,TunnelParameters,TunnelResult,simulate_tunnel
from physics_playground.simulation_cache import cached_tunnel as simulate_tunnel
from physics_playground.presentation.learning_modes import ChangedVariable,LearningMode,assumptions_panel,changed_variable_banner,comparison_metrics,mode_heading,mode_navigation
from physics_playground.presentation.notebook_ui import REUSE_REQUEST_KEY,add_trial
from physics_playground.presentation.tunnel_charts import plot_figure
from physics_playground.validation import PhysicsValidationError
from physics_playground.presentation.accessibility import render_chart
PLANETS={"Earth 🌍":(6_371_000,9.81),"The Moon 🌕":(1_737_000,1.62),"Mars 🔴":(3_390_000,3.71)};VERSION="tunnel-2.0"
def _init():
    for k,v in (("tunnel_nonce",0),("tunnel_launched",None),("tunnel_compare_nonce",0),("tunnel_compare_signature",None)):st.session_state.setdefault(k,v)
def _summary(r):
    c=st.columns(3);c[0].metric("Model",r.parameters.model.value);c[1].metric("Opposite-point time",f"{r.opposite_time_s/60:.1f} min");c[2].metric("Center speed",f"{r.maximum_speed_m_s/1000:.2f} km/s")
    st.caption(f"Text outcome: the {r.parameters.model.value.lower()} reaches the opposite turning point in {r.opposite_time_s/60:.1f} minutes and is fastest at the center.")
def _metrics(r):return {"period_s":r.period_s,"opposite_time_s":r.opposite_time_s,"maximum_speed_m_s":r.maximum_speed_m_s,"energy_drift_percent":r.energy_drift_fraction*100}
def _record(r,seed,obs,label=None,badges=()):add_trial(simulation_id="earth_tunnel",parameters=r.parameters.to_dict(),prediction=st.session_state.get("tunnel_quiz_guess"),result_summary=f"{r.parameters.model.value}: {r.opposite_time_s/60:.1f} min to opposite point",metrics=_metrics(r),earned_badges=badges,random_seed=seed,model_version=VERSION,learner_observation=obs,label=label)
def _award(r):
    return kidtools.process_run("earth_tunnel",evaluate_tunnel_missions(r))
def _reuse():
    q=st.session_state.get(REUSE_REQUEST_KEY)
    if not q or q.get("simulation_id")!="earth_tunnel":return
    p=q["parameters"];st.session_state["tunnel_custom_radius"]=int(round(float(p["radius_m"])/1000/100)*100);st.session_state["tunnel_custom_g"]=float(p["surface_gravity_m_s2"]);st.session_state["tunnel_start"]="Halfway down" if float(p["start_fraction"])<1 else "Surface";st.session_state["tunnel_model"]=p["model"];st.session_state["tunnel_planet"]="Custom planet 🪐";st.session_state["tunnel_learning_mode"]="Explore";del st.session_state[REUSE_REQUEST_KEY]
def render_explore():
    mode_heading(LearningMode.EXPLORE,"Fall through a planet");planet=st.radio("Planet",[*PLANETS,"Custom planet 🪐"],horizontal=True,key="tunnel_planet")
    if planet.startswith("Custom"):
        c1,c2=st.columns(2)
        with c1:radius_km=st.slider("Custom radius (km)",500,8000,3000,100,key="tunnel_custom_radius")
        with c2:g=st.slider("Custom surface gravity",1.0,20.0,9.81,.01,key="tunnel_custom_g")
        radius=radius_km*1000
    else:radius,g=PLANETS[planet]
    start=st.radio("Starting point",["Surface","Halfway down"],horizontal=True,key="tunnel_start");model=TunnelModel(st.selectbox("Planet interior model",[m.value for m in TunnelModel],key="tunnel_model"));gradient=.75
    if model==TunnelModel.RADIAL:gradient=st.slider("Center-to-surface density gradient",0.0,.95,.75,.05)
    p=TunnelParameters(radius,g,1 if start=="Surface" else .5,model,gradient);r=simulate_tunnel(p);_summary(r);autoplay=st.session_state.tunnel_launched==p.to_dict();canvas_kit.show(build_tunnel_canvas(r,seed=20262300+st.session_state.tunnel_nonce,autoplay=autoplay),height=PLAYER_HEIGHT)
    obs=st.text_input("Optional notebook observation",key="tunnel_observation")
    if st.button("🕳️ JUMP IN!",type="primary",use_container_width=True):st.session_state.tunnel_nonce+=1;st.session_state.tunnel_launched=p.to_dict();badges=_award(r);_record(r,20262300+st.session_state.tunnel_nonce,obs,badges=badges);st.rerun()
    kidtools.mission_checklist("The Big Fall")
def _pair(kind):
    if kind=="Surface versus halfway start":items=[("Surface",simulate_tunnel(TunnelParameters(6371000,9.81,1)),"#42A5F5"),("Halfway",simulate_tunnel(TunnelParameters(6371000,9.81,.5)),"#FF8A65")];change=ChangedVariable("Starting amplitude","Surface","Halfway")
    elif kind=="Earth versus Moon versus custom planet":items=[("Earth",simulate_tunnel(TunnelParameters(6371000,9.81)),"#42A5F5"),("Moon",simulate_tunnel(TunnelParameters(1737000,1.62)),"#B0BEC5"),("Custom",simulate_tunnel(TunnelParameters(3000000,12)),"#AB47BC")];change=ChangedVariable("Planet","Earth","Moon and custom")
    else:items=[("Uniform",simulate_tunnel(TunnelParameters(6371000,9.81,model=TunnelModel.UNIFORM)),"#42A5F5"),("Radial",simulate_tunnel(TunnelParameters(6371000,9.81,model=TunnelModel.RADIAL)),"#FF8A65")];change=ChangedVariable("Interior model","Uniform density","Radial density")
    return items,change
def render_compare():
    mode_heading(LearningMode.COMPARE,"Overlay falls");kind=st.selectbox("Comparison",["Surface versus halfway start","Earth versus Moon versus custom planet","Uniform-density versus radial-density model"]);items,change=_pair(kind);changed_variable_banner(change);sig={"kind":kind};obs=st.text_input("Optional comparison observation",key="tunnel_compare_observation")
    if st.button("▶ Run comparison",type="primary",use_container_width=True):
        st.session_state.tunnel_compare_nonce+=1;st.session_state.tunnel_compare_signature=sig;n=st.session_state.tunnel_compare_nonce
        for i,(label,r,_) in enumerate(items):_record(r,20262400+n+i,obs,f"Run {chr(65+i)} — {label}")
    canvas_kit.show(build_tunnel_comparison_canvas(items,seed=20262500+st.session_state.tunnel_compare_nonce,autoplay=st.session_state.tunnel_compare_signature==sig),height=PLAYER_HEIGHT)
    if len(items)>=2:comparison_metrics({k:(k,v) for k,v in _metrics(items[0][1]).items()},{k:(k,v) for k,v in _metrics(items[1][1]).items()})
def _latest():
    if not st.session_state.tunnel_launched:return TunnelParameters(6371000,9.81)
    d=dict(st.session_state.tunnel_launched);d["model"]=TunnelModel(d["model"]);return TunnelParameters(**d)
def render_analyze():
    mode_heading(LearningMode.ANALYZE,"Position, velocity, acceleration, and energy");r=simulate_tunnel(_latest());_summary(r)
    for plot in r.plots:fig=plot_figure(plot);render_chart(fig,f"{plot.title}; axes are {plot.x_label} and {plot.y_label}.");plt.close(fig)
def render_model():
    mode_heading(LearningMode.MODEL,"Why uniform density becomes SHM");st.latex(r"M(r)=M\left(\frac rR\right)^3")
    st.latex(r"a(r)=-\frac{GM(r)}{r^2}=-\frac{GM}{R^3}r=-\frac gRr")
    st.latex(r"\ddot r+\frac gRr=0,\quad T=2\pi\sqrt{R/g}")
    st.markdown("Uniform density makes enclosed mass grow as r³, so gravitational acceleration becomes proportional to −r: exactly the defining equation of simple harmonic motion. The radial-density model instead integrates the enclosed mass of a center-heavy profile with RK4.")
    assumptions=simulate_tunnel(TunnelParameters(6371000,9.81)).assumptions;assumptions_panel(assumptions,("Pressure, heat, and the physical feasibility of the tunnel are ignored.","The real Earth is layered and not perfectly radial.","Rotation and the Coriolis effect are omitted.","The radial profile is illustrative, not a seismological Earth model."))
def render():
    _init();_reuse();st.header("🕳️ The Big Fall");st.markdown("Default model: **uniform-density planet**. An advanced radial-density profile is also available.")
    revealed=kidtools.prediction_quiz(key="tunnel_quiz",question="About how long does the ideal uniform-density Earth fall take from one surface to the other?",options=["5 minutes","42 minutes","3 hours","Forever"],correct_index=1,reveal_text="It takes about **42 minutes** to reach the opposite surface.",mission_id="tunnel_predict")
    if not revealed:st.caption("🔬 Make your prediction before results are shown.");return
    mode=mode_navigation(key="tunnel_learning_mode");st.divider()
    try:{LearningMode.EXPLORE:render_explore,LearningMode.COMPARE:render_compare,LearningMode.ANALYZE:render_analyze,LearningMode.MODEL:render_model}[mode]()
    except PhysicsValidationError as e:st.error(f"That setup can't run yet: {e}")
