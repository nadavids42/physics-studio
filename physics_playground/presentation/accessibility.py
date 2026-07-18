"""Streamlit accessibility panel, global CSS, and chart rendering."""
from __future__ import annotations
import streamlit as st
from cycler import cycler
import matplotlib as mpl
from physics_playground.accessibility import AccessibilitySettings
from physics_playground.visual.css import streamlit_css
from physics_playground.visual.tokens import LIGHT_THEME
from physics_playground.visual.experience import DEFAULT_PRESENTATION_LEVEL,PresentationLevel

SETTINGS_KEY="accessibility_settings"
PRESENTATION_LEVEL_KEY="presentation_level"
SAFE_COLORS=LIGHT_THEME.graph_colors
LINE_STYLES=("-","--","-.",":","-","--","-.")
MARKERS=("o","s","^","D","v","P","X")
def get_accessibility_settings():
    value=st.session_state.get(SETTINGS_KEY)
    if isinstance(value,AccessibilitySettings):return value
    settings=AccessibilitySettings.from_dict(value or {});st.session_state[SETTINGS_KEY]=settings;return settings
def get_presentation_level():
    value=st.session_state.get(PRESENTATION_LEVEL_KEY,DEFAULT_PRESENTATION_LEVEL.value)
    try:return PresentationLevel(value)
    except ValueError:return DEFAULT_PRESENTATION_LEVEL
def render_accessibility_panel():
    current=get_accessibility_settings()
    with st.expander("♿ Accessibility settings"):
        reduced=st.checkbox("Reduce animation and disable autoplay",current.reduced_motion,key="access_reduce")
        contrast=st.checkbox("High-contrast display",current.high_contrast,key="access_contrast")
        large=st.checkbox("Larger interface text",current.large_text,key="access_large_text")
        st.caption("Animation controls remain available in reduced-motion mode.")
        current_level=get_presentation_level()
        level=PresentationLevel(st.selectbox("Visual presentation",[item.value for item in PresentationLevel],
            index=list(PresentationLevel).index(current_level),format_func=lambda value:value.title(),key="access_presentation_level",
            help="Diagram maximizes clarity; Illustrated adds restrained depth; Contextual adds an optional real-world setting."))
        st.session_state[PRESENTATION_LEVEL_KEY]=level.value
    updated=AccessibilitySettings(reduced,contrast,large)
    if updated!=current:
        st.session_state[SETTINGS_KEY]=updated
        try:
            from physics_playground.presentation.profile_ui import persist_active_session
            persist_active_session()
        except Exception:pass
    return updated
def apply_global_accessibility(settings):
    text_size="18px" if settings.large_text else "inherit"
    contrast="""
    .stApp { background:#000 !important; color:#fff !important; }
    .stApp [data-testid="stSidebar"] { background:#111 !important; }
    a { color:#6EC6FF !important; text-decoration:underline !important; }
    """ if settings.high_contrast else ""
    st.markdown(f"""<style>{streamlit_css()}
    html,body,.stApp {{ max-width:100%; overflow-x:hidden; font-size:{text_size}; }}
    [data-testid="stHorizontalBlock"] {{ flex-wrap:wrap; }}
    button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,[role="radio"]:focus-visible {{ outline:3px solid #0072B2 !important; outline-offset:3px !important; }}
    iframe {{ max-width:100% !important; }}
    {contrast}
    </style>""",unsafe_allow_html=True)
    mpl.rcParams["axes.prop_cycle"]=cycler(color=SAFE_COLORS)+cycler(linestyle=LINE_STYLES)+cycler(marker=MARKERS)
def render_chart(figure,caption):
    for axis in figure.axes:
        for index,line in enumerate(axis.lines):
            line.set_linestyle(LINE_STYLES[index%len(LINE_STYLES)])
            line.set_marker(MARKERS[index%len(MARKERS)])
            line.set_markevery(max(1,len(line.get_xdata())//12) if len(line.get_xdata()) else 1)
    st.pyplot(figure,use_container_width=True)
    st.caption(f"Chart description: {caption}")
