"""Compatibility wrapper for embedding shared-player documents in Streamlit.

All document generation now lives in :mod:`physics_playground.canvas.player` and
the family scene adapters.  ``show`` remains public because simulation pages
and downstream imports still use it.
"""

import streamlit as st


def show(html_doc: str, height: int = 420):
    """Embed an already-built shared-player document."""
    st.iframe(html_doc, height=height, tab_index=0)
