# Accessibility verification report

Verified: 2026-07-18 against the current Streamlit application and shared browser player.

## Scope and evidence

The application was launched with `streamlit run app.py` and loaded through headless Chromium. The
browser established a live connection to Streamlit. Stable application behavior was exercised on
the home screen and Cannonball page through Streamlit `AppTest`; the embedded player was exercised
as rendered HTML in Chromium at a 420 × 620 viewport. This avoids coupling tests to undocumented
Streamlit class names.

| Behavior | Evidence | Result |
|---|---|---|
| Keyboard order and focus visibility | Chromium traverses the player controls in play, replay, previous frame, next frame, scrubber, speed order and checks computed focus outline. | Pass |
| Play, pause, replay, step, and scrub | Browser clicks and input events verify state changes, a `Frame 2 of 3` announcement, and a meaningful `75 percent` scrub value. Vitest covers state boundaries and teardown. | Pass |
| Native control keyboard behavior | Browser/Vitest verify that Space on a focused form control is not intercepted by the document playback shortcut. | Fixed and passing |
| Screen-reader names | Browser checks names for all six player controls, the named canvas, control-group role, and polite live region. | Pass at DOM/accessibility-semantics level |
| Live announcements | Player reports ready, reduced-motion, playing, paused, frame, percentage, and completion states through a polite status region. | Pass |
| Reduced motion | Chromium verifies autoplay suppression; particles and camera transitions have behavioral unit coverage. Controls remain available. | Pass |
| High contrast and large text | Chromium verifies the applied classes and focus treatment; representative high-contrast optics and mobile scenes have perceptual baselines. | Pass |
| Color-independent graphs | Chart contract tests require different line styles and markers, accessible descriptions, and a keyboard-focusable data table. | Pass |
| Narrow layout | Chromium verifies no horizontal document overflow at 420 px; player controls wrap and existing mobile visual baselines pass. | Pass |
| Iframe focus | Player iframes now request `tab_index=0`; inner controls have their own deterministic focus order. | Pass within Streamlit API limits |
| Error messaging | `AppTest` drives a projectile beyond its maximum-time window and verifies an actionable visible error telling the learner how to recover. | Pass |
| Accessibility preferences | `AppTest` enables reduced motion, high contrast, and larger text together and verifies structured state persistence without hiding navigation. | Pass |

Automated evidence lives in:

- `tests/test_browser_accessibility.py`
- `tests/test_streamlit_app.py`
- `frontend/test/player-runtime.test.js`
- `tests/test_interactive_charts.py`
- `tests/test_visual_screenshots.py`

## Confirmed fixes

1. The animation controls now use an explicitly named `role="group"`.
2. The scrubber exposes percentages through `aria-valuetext` instead of only its internal 0–1000
   range.
3. Global player shortcuts no longer intercept Space while a button, select, or range input owns
   focus. Native keyboard activation is preserved.
4. Embedded simulation iframes explicitly participate in keyboard order through Streamlit's public
   `tab_index` parameter.
5. Three unnecessary `!important` declarations were removed from focus and iframe sizing rules.
   The remaining declarations enforce user-selected high contrast over Streamlit theme rules or
   reduced motion over authored transitions.

## Framework limitations

- The installed `st.iframe` API supports `tab_index` but does not expose a `title` argument. The
  embedded document and canvas are named, but the outer iframe's accessible name remains controlled
  by Streamlit. Revisit this when Streamlit adds a supported title/name parameter; do not patch its
  generated DOM with a fragile selector.
- Streamlit owns shell markup, sidebar disclosure behavior, and much of the outer focus order.
  Automated tests use public widget labels and state rather than generated Emotion class names.
- Headless Chromium can verify accessibility semantics but is not a substitute for speech output
  from NVDA, VoiceOver, or Orca.
- Focus transfer into and out of a cross-document iframe varies slightly by browser and assistive
  technology even when both documents have correct tab order.

## Manual release checks

The following checks cannot be made reliable in the current headless harness. Record browser,
operating system, assistive technology, and outcome when completing them for a release:

- [ ] NVDA + Firefox or Chrome: read the home hierarchy, open Cannonball, enter the player iframe,
  operate every control, and confirm live announcements are useful rather than repetitive.
- [ ] VoiceOver + Safari: verify sidebar disclosure, iframe entry/exit, rotor names, chart
  descriptions, and error announcement.
- [ ] Keyboard only: traverse home, accessibility settings, a lesson, all four simulation modes,
  player controls, interactive chart table, and return navigation without focus loss.
- [ ] Browser zoom at 200% and 400%: verify large-text mode, 320 CSS-pixel reflow, no clipped labels,
  and no two-dimensional scrolling except intentionally scrollable data tables.
- [ ] Windows High Contrast/forced-colors: verify native controls, focus indicator, vector labels,
  graph line styles, and selected states remain distinguishable.
- [ ] Cognitive review: confirm live status messages do not announce continuously during playback
  and recovery text describes the next action in plain language.

## Running the automated checks

```bash
npm --prefix frontend test
pytest -q tests/test_streamlit_app.py tests/test_interactive_charts.py
CHROMIUM_BIN=/path/to/chromium pytest -q tests/test_browser_accessibility.py
CHROMIUM_BIN=/path/to/chromium pytest -q tests/test_visual_screenshots.py
```
