"""Registry-driven Streamlit application shell."""
from __future__ import annotations
from importlib import import_module
import streamlit as st
from physics_playground.missions import legacy as kidtools
from physics_playground.presentation.home import render_home
from physics_playground.presentation.notebook_ui import render_notebook_sidebar
from physics_playground.presentation.profile_ui import persist_active_session,render_profile_sidebar
from physics_playground.presentation.accessibility import apply_global_accessibility,render_accessibility_panel
from physics_playground.presentation.diagnostics import render_developer_diagnostics
from physics_playground.registry import SIMULATION_REGISTRY,SIMULATIONS_BY_ID
from physics_playground.validation import PhysicsValidationError

st.set_page_config(page_title="Physics Mission Control",page_icon="🚀",layout="wide")
kidtools.init_missions();st.session_state.setdefault("active_simulation_id",None)
with st.sidebar:
    render_profile_sidebar();st.divider()
    accessibility_settings=render_accessibility_panel();st.divider()
    st.header("🎮 Mission navigation")
    navigation=["home",*[item.id for item in SIMULATION_REGISTRY]]
    current=st.session_state.active_simulation_id or "home"
    if "registry_navigation" not in st.session_state:
        st.session_state.registry_navigation=current if current in navigation else "home"
    selected=st.radio("Destination",navigation,
        format_func=lambda value:"🏠 Mission Control" if value=="home" else SIMULATIONS_BY_ID[value].navigation_label,
        label_visibility="collapsed",key="registry_navigation")
    st.session_state.active_simulation_id=None if selected=="home" else selected
    st.divider();st.subheader("🏅 Badge collection");kidtools.sidebar_badges()
    total=len(kidtools.MISSION_LABELS)
    if len(st.session_state.missions)==total:st.success("🏆 ALL BADGES EARNED! You are officially a Physics Champion!")
    st.divider();render_notebook_sidebar();render_developer_diagnostics()

apply_global_accessibility(accessibility_settings)

active=st.session_state.active_simulation_id
if active is None:render_home()
else:
    definition=SIMULATIONS_BY_ID[active]
    module=import_module(definition.page_module)
    try:
        module.render()
    except (PhysicsValidationError,FloatingPointError,OverflowError,MemoryError) as error:
        st.error("This experiment could not finish safely. Try smaller values, fewer steps, or the recommended time step.")
        with st.expander("Technical details"):
            st.code(f"{type(error).__name__}: {error}")

persist_active_session()
