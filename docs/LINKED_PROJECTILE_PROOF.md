# Linked projectile representation proof

## Scope and decision

The Cannonball Analyze and Compare modes now use one browser document containing the canvas,
trajectory, position/velocity/acceleration graphs, governing equations, controls, and accessible
readout. One `LinkedProjectileRuntime` owns the time fraction. Scrubbing, graph pointing, graph
keyboard commands, stepping, and playback all update that shared clock without a Streamlit rerun.

This validates an iframe as a temporary delivery boundary for a self-contained interactive
experience. It invalidates the previous composition of separate player and chart iframes for
representations that must coordinate: independent documents cannot share hover, selection,
focus, axis domains, or animation time without an additional cross-frame protocol. The same
runtime can later mount as a first-class web component; its state and interaction logic do not
depend on Streamlit.

## Data and interaction boundary

Python remains authoritative. `ProjectileResult.animation` supplies time and position samples;
the Python adapter derives velocity and acceleration arrays with the same sampled timeline and
serializes finite JSON. It caps the presentation payload at 120 evenly selected result samples,
preserving endpoints. JavaScript interpolates or selects these supplied values but does not rerun
the physical model.

Comparison runs share domains computed from both payload runs. Horizontal quantities are purple,
vertical quantities red, and comparison identity uses solid/dashed lines plus labels, so color is
not the only distinction. Equation-term buttons highlight the corresponding position, velocity,
or acceleration graphs.

Reduced-motion mode disables autoplay while preserving the scrubber, single-sample step buttons,
graph arrow keys, Home, and End. Every inspected state is announced as time, x, y, vx, vy, ax,
and ay with units. Graphs and equation terms are keyboard focusable and named.

## Measurements

Measured on the representative 20 m/s, 30° versus 60° comparison with source results containing
240 samples each:

| Measure | Result |
| --- | ---: |
| Linked samples after presentation downsampling | 120 per run |
| Two-run JSON payload | 43,539 bytes |
| Bundled linked runtime, including shared player and Cannonball scene | 76,043 bytes |
| Complete cached iframe document | 131,742 bytes |
| Browser seek/update benchmark | under 16.7 ms average across 100 seeks |
| Streamlit reruns for scrub, graph hover/select, equation selection, or keyboard step | 0 |
| Iframes used by the linked experience | 1 |

The Python document cache returns the identical document for unchanged physical results, so an
unrelated Streamlit rerun does not change the iframe source document. A changed physical payload
correctly produces a different document and remount boundary.

## Limits

This is not a generic plotting framework and does not migrate other simulations. The iframe still
isolates focus and layout from the surrounding page, duplicates bundled code in its HTML, and
cannot participate directly in application-level routing or state. The proof supports keeping a
single coordinated iframe during the Streamlit phase, while strengthening the case for mounting
the same runtime directly in the future web frontend.
