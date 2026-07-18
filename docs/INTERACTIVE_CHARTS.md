# Interactive charts

Physics Studio keeps Matplotlib as its static scientific-chart renderer and adds a small
browser-native layer only where interaction supports a learning action or avoids a costly image
rerender.

## Selection audit

Charts are strong interactive candidates when learners need to inspect exact sampled values,
compare multiple runs at a shared coordinate, focus one series across chart and table, or zoom into
a threshold, resonance, asymptote, or local maximum. Representative candidates include projectile
trajectory comparisons, range and approximation-error scans, resonance curves, phase-space
comparisons, collision position overlays, and field/potential line scans.

Static charts remain preferable for short single-series summaries, charts used primarily as a
printable model reference, and views where hover or zoom adds no instructional task. Existing
energy histories and basic diagnostic plots remain Matplotlib charts during this proof stage.

## Contract

Vertical slices define `InteractiveChart` values from `physics_playground.models.charts`. The
contract is independent of Streamlit and JavaScript and contains:

- a stable chart ID, title, and textual description;
- separate axis labels and units;
- immutable numerical series;
- semantic color roles from the shared colorblind-safe graph palette;
- line style and marker shape, so color is never the only series encoding;
- explicit hover, linked-highlight, zoom, and table capabilities.

Slice chart adapters translate immutable model results into this contract, then call
`render_interactive_chart(chart)`. Physics modules must not import the renderer or construct UI.

## Accessibility and behavior

Every interactive chart includes SVG `title` and `desc` elements and an optional native data table.
Table rows are keyboard focusable and linked to the same series emphasis used by pointer hover.
Series legends state line style and marker shape. Axis units remain visible in the SVG and table.
Zoom is optional and always has a reset control. The textual description remains available even if
client-side interaction is unavailable.

## Performance measurement

On the representative Cannonball range scan, local Python-side measurements were:

| Rendering preparation | Time |
| --- | ---: |
| Matplotlib figure construction | 66.89 ms |
| Interactive document, cold | 0.42 ms |
| Interactive document, cached | 0.36 ms |

The interactive document was about 13 KB and rendering/hover work moves to the browser. These are
development-machine measurements, not cross-device guarantees. Pure scan arrays remain cached by
complete physical inputs, while interactive documents use a bounded 128-entry payload cache.

## Migration rule

Do not mechanically replace repository charts. For each chart, name the learner interaction first,
retain a textual and tabular alternative, test units and deterministic samples, and compare browser
cost with the current static rendering. If no useful interaction exists, keep the static chart.
