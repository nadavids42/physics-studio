"""CSS generation for Streamlit and embedded simulation documents."""
from dataclasses import asdict
from physics_playground.visual.tokens import DARK_THEME, LIGHT_THEME, MOTION, RESPONSIVE, SHAPE, SPACING, TYPOGRAPHY


def _variables(theme) -> str:
    colors = ";".join(f"--ps-{name.replace('_','-')}:{value}" for name, value in asdict(theme).items() if name != "name")
    return colors + ";"


LIGHT_VARS = _variables(LIGHT_THEME)
DARK_VARS = _variables(DARK_THEME)


def shared_css() -> str:
    """Framework-neutral tokens, typography, motion, and responsive rules."""
    return f"""
:root {{{LIGHT_VARS}
  --ps-font-ui:{TYPOGRAPHY.family_ui};--ps-font-equation:{TYPOGRAPHY.family_equation};
  --ps-font-numeric:{TYPOGRAPHY.family_numeric};--ps-radius-sm:{SHAPE.radius_small}px;
  --ps-radius-md:{SHAPE.radius_medium}px;--ps-radius-lg:{SHAPE.radius_large}px;
  --ps-radius-panel:{SHAPE.radius_panel}px;--ps-shadow-low:{SHAPE.shadow_low};
  --ps-shadow-medium:{SHAPE.shadow_medium};--ps-duration-fast:{MOTION.fast_ms}ms;
  --ps-duration-standard:{MOTION.standard_ms}ms;--ps-ease-standard:{MOTION.ease_standard};
  color-scheme:light dark;
}}
@media (prefers-color-scheme:dark) {{:root {{{DARK_VARS}}}}}
[data-ps-theme="light"] {{{LIGHT_VARS}}}
[data-ps-theme="dark"] {{{DARK_VARS}}}
html,body {{font-family:var(--ps-font-ui);color:var(--ps-text);}}
.ps-heading {{font-size:{TYPOGRAPHY.heading_medium}px;line-height:{TYPOGRAPHY.line_height_tight};font-weight:{TYPOGRAPHY.weight_semibold};}}
.ps-label {{font-size:{TYPOGRAPHY.label}px;font-weight:{TYPOGRAPHY.weight_semibold};}}
.ps-annotation {{font-size:{TYPOGRAPHY.annotation}px;color:var(--ps-text-muted);}}
.ps-helper {{font-size:{TYPOGRAPHY.helper}px;color:var(--ps-text-muted);}}
.ps-equation {{font-family:var(--ps-font-equation);}}
.ps-numeric {{font-family:var(--ps-font-numeric);font-variant-numeric:tabular-nums;}}
.ps-surface {{background:var(--ps-surface);border:1px solid var(--ps-border);border-radius:var(--ps-radius-panel);box-shadow:var(--ps-shadow-low);}}
button,input,select,a {{transition:background-color var(--ps-duration-standard) var(--ps-ease-standard),border-color var(--ps-duration-standard) var(--ps-ease-standard),color var(--ps-duration-standard) var(--ps-ease-standard),box-shadow var(--ps-duration-standard) var(--ps-ease-standard);}}
:focus-visible {{outline:3px solid var(--ps-focus);outline-offset:3px;}}
img,svg,canvas,iframe {{max-width:100%;}}
@media (max-width:{RESPONSIVE.tablet_max_px}px) {{.ps-heading {{font-size:{TYPOGRAPHY.heading_small}px;}}}}
@media (max-width:{RESPONSIVE.mobile_max_px}px) {{.ps-label {{font-size:{TYPOGRAPHY.annotation}px;}}.ps-annotation {{font-size:{TYPOGRAPHY.helper}px;}}}}
@media (prefers-reduced-motion:reduce) {{*,*::before,*::after {{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;}}}}
"""


def streamlit_css() -> str:
    return shared_css() + f"""
.stApp {{background:var(--ps-canvas);color:var(--ps-text);}}
.stApp [data-testid="stSidebar"] {{background:var(--ps-surface);border-right:1px solid var(--ps-border);}}
.stApp [data-testid="stMetric"],.stApp [data-testid="stExpander"] {{border-radius:var(--ps-radius-lg);}}
.stApp p,.stApp label {{line-height:{TYPOGRAPHY.line_height_body};}}
.stApp iframe {{width:100%;border:0;border-radius:var(--ps-radius-panel);}}
@media (max-width:{RESPONSIVE.mobile_max_px}px) {{.stApp [data-testid="stHorizontalBlock"] {{gap:{SPACING.sm}px;}}}}
"""
