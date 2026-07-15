"""Reusable Streamlit lab-report selection and export controls."""
import streamlit as st
from physics_playground.presentation.profile_ui import current_scientist_name
from physics_playground.registry import SIMULATIONS_BY_ID
from physics_playground.reports import generate_report_bundle
def render_report_builder(notebook):
    st.markdown("##### 🧪 Generate lab report")
    if not notebook.trials:st.info("Complete an experiment before generating a report.");return
    simulations=sorted({t.simulation_id for t in notebook.trials});simulation=st.selectbox("Report simulation",simulations,format_func=lambda value:SIMULATIONS_BY_ID[value].title,key="report_simulation")
    trials=notebook.filtered(simulation);labels={t.id:f"Trial #{t.trial_number} — {t.label or t.result_summary}" for t in trials}
    selected=st.multiselect("Trials to include",list(labels),format_func=labels.get,key="report_trials")
    if st.button("Generate report",disabled=not selected,type="primary",use_container_width=True,key="generate_report"):
        try:st.session_state.generated_lab_report=generate_report_bundle(notebook,selected,current_scientist_name())
        except ValueError as error:st.error(str(error))
    bundle=st.session_state.get("generated_lab_report")
    if not bundle or bundle.report.simulation_id!=simulation:return
    st.success(f"Report ready: {bundle.report.simulation_title}, {len(bundle.report.trials)} trial(s)")
    st.markdown(f"**Question:** {bundle.report.question}")
    st.download_button("Download printable HTML",bundle.html,"physics-lab-report.html","text/html",use_container_width=True)
    st.download_button("Download Markdown",bundle.markdown,"physics-lab-report.md","text/markdown",use_container_width=True)
    st.download_button("Download report CSV",bundle.csv,"physics-lab-report.csv","text/csv",use_container_width=True)
    st.download_button("Download report JSON",bundle.json,"physics-lab-report.json","application/json",use_container_width=True)
