# Mechanics experience hardening baseline

Measured on 2026-07-18 in the local development environment. Timings are diagnostic
samples, not portable performance guarantees or CI thresholds.

## Measurements

| Measure | Result | Method |
|---|---:|---|
| Initial application load | 2,343 ms | Cold Streamlit `AppTest` run |
| Cannonball lesson load | 210 ms | Warm direct lesson route with `AppTest` |
| Cannonball model execution | 0.246 ms median; 0.391 ms p95 | 100 analytic runs, 240 result samples |
| Linked payload | 43,555 bytes | Two comparison runs, compact JSON, 120 samples per run |
| Linked document | 135,798 bytes | Complete generated single-runtime HTML document |
| Linked JavaScript bundle | 79,443 bytes | Deterministic production asset after this pass |
| Linked seek/update work | below one 16.7 ms frame | 100 seeks in headless Chromium; enforced by browser test |
| Cached-document memory delta | 394,744 bytes | `tracemalloc`, 100 repeated document requests |
| Narrow-screen overflow | none at 320 CSS px | Headless Chromium with the comparison experience |

The cold and warm load figures include test-harness overhead and are retained only as
a reproducible local baseline. They are deliberately not CI budgets. The physics timing
is far below rendering and framework overhead, so no model optimization was justified.

## Reruns and mounts

- Scrubbing, graph selection, equation selection, playback, and keyboard stepping occur
  within the single linked frontend runtime: zero Streamlit reruns.
- A Streamlit widget or submitted form causes one normal Streamlit rerun.
- An unrelated rerun produces an identical cached linked document and does not request a
  new player mount. A changed physical result produces one bootstrap mount for the new
  document.
- The runtime now has an idempotent `destroy()` path that removes its listeners and
  destroys the player on page teardown. The document cache remains bounded to 32 entries.

## Findings and fixes

Automated inspection found that comparison plots could become color-dependent in forced
colors, and that the continuously updating result readout was an overly aggressive live
region. Components and comparison runs now use distinct line patterns that survive forced
colors. The visible readout remains available at all times, while a separate polite live
region announces only committed pointer, scrubber, and keyboard selections rather than
every animation frame. Listener teardown was added to bound memory when this runtime is
mounted directly by a future frontend.

The Chromium audit covers keyboard graph operation, accessible labels and value text,
reduced-motion state, forced colors/high contrast, a 320 px viewport, color-independent
line patterns, a single canvas/clock, teardown, overflow, and frame work. Existing visual
tests cover light and dark themes; player tests cover large-text and high-contrast modes.

## Stable CI budgets

`tests/test_mechanics_experience_budgets.py` enforces a linked bundle no larger than
85,000 bytes, a representative two-run payload no larger than 50,000 bytes, at most 120
samples per run, deterministic cached documents, one bootstrap mount, and bounded cache
size. These are deterministic size and lifecycle properties. Hardware-sensitive app-load,
model-time, memory-allocation, and frame-time regressions remain measured diagnostics;
only the browser's per-interaction frame-work check uses a frame boundary.

## Required manual accessibility checks

Automation is not a substitute for these checks before a release:

1. Traverse the full lesson and simulation using only Tab, Shift+Tab, arrows, Enter,
   Space, Home, and End; verify focus order, visible focus, dialogs/forms, and escape paths.
2. Complete the lesson with NVDA/Firefox or NVDA/Chrome and VoiceOver/Safari (Orca/Firefox
   is useful on Linux); verify heading navigation, landmarks, controls, equations, graph
   descriptions, announcements, errors, and restored answers.
3. At 200% and 400% browser zoom, verify reflow, reading order, no clipped content, and no
   two-dimensional scrolling except where the scientific visual itself requires it.
4. Enable the operating system's reduced-motion setting and verify there is no autoplay,
   every state remains manually inspectable, and focus does not move unexpectedly.
5. Exercise native high-contrast and forced-colors modes, not only CSS emulation; verify
   controls, focus, selected state, target, trajectories, and graph series remain distinct.
6. Check light and dark modes for readable text, equations, callouts, disabled controls,
   diagrams, and focus indicators.
7. Increase the OS and browser default text size without zoom; verify labels wrap and no
   control or status text is truncated.
8. Test a real touch phone and a narrow desktop viewport in portrait and landscape; verify
   target sizes, sticky/fixed regions, the keyboard, scrolling, and orientation changes.
9. Ask a keyboard and screen-reader user to distinguish every graph component and run
   without naming colors; confirm patterns, labels, legend, and time/value readout convey
   equivalent information.

These automated and manual procedures do **not** establish or claim WCAG conformance.
Formal conformance evaluation, assistive-technology user testing, content review, and
issue-by-issue remediation remain required.
