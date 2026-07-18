# Frontend extraction plan

## Current foundation

Physics Studio now has a framework-free frontend workspace in `frontend/`. Authored JavaScript is
written as small ES modules under `frontend/src/`, tested with Vitest, linted with ESLint, formatted
with Prettier, and bundled with esbuild. Built browser assets are committed under
`physics_playground/static/js/` so a normal Python installation and Streamlit deployment do not
need Node.js.

The shared player runtime, canvas primitives, scientific assets, vector annotations, animation
effects, and experience helpers now live in `frontend/src`. `player-runtime.js` is the composition
root. It installs the temporary browser globals consumed by inline scene adapters, while the
modules themselves use explicit imports and exports. Python compatibility constants load built
package assets and contain no editable JavaScript.

Each iframe receives one copy of the composed player bundle. This removes the former duplication of
six separately concatenated libraries inside a document. Browser security isolation prevents
sibling Streamlit component iframes from safely sharing one live global runtime; changing that
would require a versioned component or external-asset delivery contract. The committed bundle is
therefore the smallest safe loading strategy during this transition.

## Responsibilities

```text
frontend/
  src/                 authored ES modules
  src/scenes/          shared and subject-colocated scene adapters
  test/                executable Vitest tests
  scripts/build.mjs    deterministic esbuild entrypoint
  eslint.config.js     JavaScript correctness rules
  package.json         contributor commands and pinned dependency ranges

physics_playground/
  frontend_assets.py   safe, cached package-resource loader
  static/js/           committed production build artifacts
  canvas/player.py     validated payload serialization and transitional iframe assembly
```

Source modules should expose one coherent responsibility. Browser globals may be assigned only at
the compatibility boundary while legacy scene scripts still consume globals. New internal module
dependencies should use ES imports.

## Development and production workflow

Install and check the frontend:

```bash
cd frontend
npm ci
npm run check
```

During development, edit only `frontend/src` and run `npm run build`. Commit the corresponding
asset change. `npm run build:check` fails when the committed artifact is missing or stale. CI runs
formatting, linting, Vitest, and the stale-build check before Python jobs complete.

Production and ordinary Python development load committed assets through `importlib.resources`.
They do not invoke npm, esbuild, or a development server. The assets are declared as setuptools
package data and remain available from wheels and source distributions.

## Payload compatibility

Python remains authoritative for immutable trajectory data, themes, accessibility settings, and
scene configuration. `build_player_document()` continues to serialize the existing JSON object and
places that payload beside the single built runtime in the iframe document. JavaScript validates
the browser-facing minimum contract before mounting and owns playback, interaction, resizing, and
rendering. Extraction does not change payload fields, numerical arrays, units, seeds, or
interpolation semantics.

## Staged migration

1. **Foundation — complete.** Maintain the ES-module workspace, deterministic build, static loader,
   CI checks, and packaged static assets.
2. **Shared runtime — complete.** Canvas primitives, vectors, experience/context helpers,
   animation helpers, scientific assets, playback state, controls, stable timestep handling, DPR
   sizing, visibility pause, announcements, keyboard input, and teardown are authored modules.
   Vitest covers playback, stepping, scrubbing, reduced motion, malformed input, and teardown.
3. **Asset decomposition — optional.** Split the large scientific asset module by scientific domain
   only when ownership or bundle measurements justify it. Preserve `PhysicsAssets` meanwhile.
5. **Scene adapters.** Move simulation-specific scene strings from slice `scene.py` files into
   subject/simulation frontend modules. **Complete:** Python scene modules serialize data and load
   named built assets rather than containing editable JavaScript.
6. **Assembly consolidation.** Replace transitional string concatenation with a versioned player
   bundle plus explicit scene registration. Keep Streamlit iframe embedding and progressive static
   fallbacks.
7. **Cleanup.** Remove compatibility globals and Python JavaScript exports only after repository-wide
   searches and tests prove no consumers remain.

## Verification required for every extraction

- ESLint, Prettier, Vitest, and deterministic build checks pass.
- A JavaScript runtime test covers the migrated behavior.
- Python tests prove the built asset is packaged and loaded safely.
- Player payload and deterministic rendering inputs remain unchanged.
- Reduced motion, high DPI, keyboard controls, narrow layouts, and theme behavior remain covered.
- No editable JavaScript copy remains in Python after its compatibility constant is migrated.

This plan deliberately avoids React, a game engine, a development server dependency, or a complex
asset manifest. Those can be reconsidered only if later scene composition demonstrates a concrete
need.

## Visual regression baselines

The intentional browser set contains five cases covering mechanics, oscillation, optics, both
themes, high contrast, reduced motion, and a narrow viewport. Chromium renders each case and Pillow
compares a perceptual difference hash plus mean color. This tolerates minor antialiasing differences
without accepting meaningful composition or theme regressions; it does not create a large set of
pixel-perfect screenshots.

To inspect a visual change, run:

```bash
CHROMIUM_BIN=/path/to/chromium pytest tests/test_visual_screenshots.py
```

If the change is intentional, render and inspect every case, then update the compact baseline:

```bash
PHYSICS_UPDATE_VISUAL_BASELINES=1 CHROMIUM_BIN=/path/to/chromium \
  pytest tests/test_visual_screenshots.py
git diff -- tests/visual_baselines.json
CHROMIUM_BIN=/path/to/chromium pytest tests/test_visual_screenshots.py
```

Never update the baseline merely to make CI green. The dedicated CI job installs Chromium and runs
the visual set together with the Streamlit `AppTest` smoke coverage on every pull request and push.
