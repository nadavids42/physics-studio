"""Streamlit adapter for the browser-native interactive chart contract."""

from __future__ import annotations

import html
import json
import time
from functools import lru_cache

import streamlit as st

from physics_playground.application_callbacks import get_player_preferences
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.models.charts import InteractiveChart
from physics_playground.performance import record_timing

CHART_JS = load_javascript_asset("interactive-chart.js")


@lru_cache(maxsize=128)
def _chart_document(payload: str, title: str, description: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{margin:0;font-family:Inter,system-ui,sans-serif;color:#152536;background:transparent}}
.chart-shell{{border:1px solid #B8C5D1;border-radius:14px;padding:10px;background:#fff}}
h3{{margin:0 0 4px}} .description{{margin:0 0 6px;color:#526577;font-size:13px}}
svg{{display:block;width:100%;height:auto;min-height:260px}} .grid{{stroke:#526577;opacity:.18}}
.axis{{stroke:#526577}} .series{{fill:none;stroke-width:2.5}} .point{{stroke-width:2}}
.muted{{opacity:.22}} .tooltip{{position:absolute;display:none;padding:6px 8px;background:#152536;color:#fff;border-radius:6px;font-size:12px;pointer-events:none}}
.chart-wrap{{position:relative}} table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}}
th,td{{padding:6px;border-bottom:1px solid #D9E1E8;text-align:right}} th:first-child,td:first-child{{text-align:left}}
tr:focus{{outline:3px solid #005FCC;outline-offset:-2px}} .controls{{display:flex;gap:8px;justify-content:flex-end}}
button{{min-height:38px;border:1px solid #B8C5D1;border-radius:8px;background:#fff;color:#152536}}
@media(prefers-color-scheme:dark){{body{{color:#F3F7FB}}.chart-shell,button{{background:#142235;color:#F3F7FB;border-color:#6F8499}}.axis,.grid{{stroke:#C0CEDA}}th,td{{border-color:#40566D}}}}
body.high-contrast{{color:#fff;background:#000}}body.high-contrast .chart-shell,body.high-contrast button{{color:#fff;background:#000;border:2px solid #fff}}body.high-contrast .description{{color:#fff}}
</style></head><body><section class="chart-shell" aria-label={json.dumps(title)}>
<h3>{html.escape(title)}</h3><p class="description">{html.escape(description)}</p>
<div class="controls"><button id="zoom-reset" type="button">Reset zoom</button></div>
<div class="chart-wrap"><svg id="chart" viewBox="0 0 720 390" role="img" aria-labelledby="chart-title chart-desc">
<title id="chart-title">{html.escape(title)}</title><desc id="chart-desc">{html.escape(description)}</desc></svg>
<div class="tooltip" id="tooltip" role="status" aria-live="polite"></div></div>
<div id="table"></div></section><script>{CHART_JS}\nmountInteractiveChart({payload});</script></body></html>"""


def build_chart_document(chart: InteractiveChart) -> str:
    preferences = get_player_preferences()
    payload_data = {
        **chart.to_dict(),
        "theme": preferences.theme,
        "high_contrast": preferences.high_contrast,
    }
    payload = json.dumps(payload_data, allow_nan=False, separators=(",", ":"))
    before = _chart_document.cache_info()
    started = time.perf_counter()
    document = _chart_document(payload, chart.title, chart.description)
    after = _chart_document.cache_info()
    record_timing(
        "chart.interactive.document",
        time.perf_counter() - started,
        "cache_hit" if after.hits > before.hits else "computed",
    )
    return document


def render_interactive_chart(chart: InteractiveChart, *, height: int = 560) -> None:
    """Render an interactive chart with its built-in accessible data table."""

    st.iframe(build_chart_document(chart), height=height, tab_index=0)
    st.caption(
        "Interactive chart. Exact values are also available in the keyboard-accessible table."
    )


def interactive_chart_cache_info():
    return _chart_document.cache_info()
