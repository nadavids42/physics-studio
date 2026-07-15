"""Registry-driven Physics Mission Control home screen."""
from __future__ import annotations
import streamlit as st
from physics_playground.missions.definitions import MISSION_DEFINITIONS
from physics_playground.models.simulations import Difficulty,SimulationDefinition
from physics_playground.registry import SIMULATION_REGISTRY

def _progress(definition:SimulationDefinition)->tuple[int,int,float]:
    earned=sum(1 for mission in MISSION_DEFINITIONS.values() if mission.group==definition.mission_group and mission.id in st.session_state.missions)
    total=definition.badge_count;return earned,total,(earned/total if total else 0)
def _filtered():
    concepts=sorted({concept for item in SIMULATION_REGISTRY for concept in item.concepts});types=sorted({item.simulation_type for item in SIMULATION_REGISTRY})
    c1,c2,c3,c4=st.columns(4)
    with c1:concept=st.selectbox("Concept",["All concepts",*concepts])
    with c2:difficulty=st.selectbox("Difficulty",["All levels",*[item.value for item in Difficulty]])
    with c3:status=st.selectbox("Progress",["All missions","Completed","Incomplete"])
    with c4:kind=st.selectbox("Simulation type",["All types",*types])
    result=[]
    for item in SIMULATION_REGISTRY:
        _,_,fraction=_progress(item)
        if concept!="All concepts" and concept not in item.concepts:continue
        if difficulty!="All levels" and item.difficulty.value!=difficulty:continue
        if status=="Completed" and fraction<1:continue
        if status=="Incomplete" and fraction>=1:continue
        if kind!="All types" and item.simulation_type!=kind:continue
        result.append(item)
    return result
def _card(item:SimulationDefinition)->None:
    earned,total,fraction=_progress(item);visual=item.visual
    with st.container(border=True):
        st.markdown(f"### {item.icon} {item.title}")
        st.markdown(f"**{item.central_question}**")
        st.write(item.description)
        st.caption(f"{item.difficulty.value} · {item.simulation_type} · {item.renderer}")
        st.markdown(" · ".join(f"`{concept}`" for concept in item.concepts))
        st.progress(fraction,text=f"{earned}/{total} badges · {fraction:.0%} complete")
        if visual:st.caption(f"{visual.symbol} {visual.thumbnail_alt}")
        label="Continue" if earned else "Start"
        def open_simulation()->None:
            st.session_state.active_simulation_id=item.id
            st.session_state.registry_navigation=item.id
        st.button(f"{label} {item.title}",key=f"home_open_{item.id}",type="primary",use_container_width=True,
                  on_click=open_simulation)
def render_home()->None:
    st.title("🚀 Physics Mission Control")
    st.caption(f"{len(SIMULATION_REGISTRY)} missions. Big questions. Guess first—then find out. You're the scientist.")
    st.markdown("## Choose your next experiment")
    items=_filtered()
    if not items:st.info("No missions match those filters.");return
    columns=st.columns(2)
    for index,item in enumerate(items):
        with columns[index%2]:_card(item)
