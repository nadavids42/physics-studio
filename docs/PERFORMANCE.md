# Interaction performance

Physics Studio optimizes within Streamlit rather than bypassing its rerun model. Physics results,
notebook records, and player payloads remain deterministic and parameter-keyed.

## Measured representative baseline

Measurements were taken locally with Python 3.11 and Streamlit 1.59.2. They are diagnostic, not a
cross-machine performance promise.

| Cannonball operation | Before | After |
| --- | ---: | ---: |
| No-drag angle scan, cold | 19.94 ms | 19.23 ms |
| Same angle scan, cached | 0.002 ms | 0.001 ms |
| Range chart construction | 48.25 ms | 46.50 ms |
| Player document, cold | 1.93 ms | 1.88 ms |
| Same player document, cached | 1.69 ms | 1.64 ms |

The principal improvement is interaction-level rather than numerical: three launch controls
previously caused three full application reruns while being adjusted. They now commit together in
one form submission. Editing the notebook observation runs an independent fragment and keeps the
player document stable.

## Repository-wide pattern

- Group parameters in a form when partial combinations have no useful pedagogical meaning.
- Keep continuous controls for graph exploration where immediate feedback is the activity.
- Place unrelated notes or secondary actions in fragments when they would otherwise remount a
  costly visualization.
- Key forms and widgets with `simulation_key` or `feature_key` and restore those exact keys from
  notebook/profile handoffs.
- Cache immutable physics results and pure scan arrays by complete physical parameters. Never
  cache session state, mutable notebook objects, open figures, or Streamlit containers.
- Rebuild Matplotlib figures from cached pure data and close them after rendering.
- Keep bounded caches. Simulation calls and player documents use 128 entries; the 64-entry
  frontend-asset cache holds the complete current built-asset catalog without read/evict churn.
- A changed physical payload must produce a changed player document. Cache tests explicitly guard
  this to prevent stale-result bugs.

All simulation page renders now record `page.<simulation_id>` timings. Player-document generation
records whether it was computed or served from cache, and chart operations may add focused timing
records. Developer diagnostics show the latest bounded samples and their source.

## Applying the pattern

Cannonball Explore is the reference implementation. Apply forms to another page only after
confirming that intermediate slider feedback is not itself educational. Analyze scans should use
cached pure functions when model execution is material; cheap list transformations can remain
direct. This avoids adding cache complexity where rerendering the chart dominates computation.
