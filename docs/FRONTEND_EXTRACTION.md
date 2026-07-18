# Frontend extraction plan

## Current foundation

Physics Studio now has a framework-free frontend workspace in `frontend/`. Authored JavaScript is
written as small ES modules under `frontend/src/`, tested with Vitest, linted with ESLint, formatted
with Prettier, and bundled with esbuild. Built browser assets are committed under
`physics_playground/static/js/` so a normal Python installation and Streamlit deployment do not
need Node.js.

The proof of concept migrates `PhysicsVisuals`, the shared canvas-primitives utility. Its editable
source is `frontend/src/physics-visuals.js`; `physics_playground/visual/primitives.py` now contains
only a compatibility export loaded through `physics_playground.frontend_assets`. The iframe still
receives the same `CANVAS_VISUAL_JS` string and the existing Python-to-player JSON payload contract
is unchanged.

## Responsibilities

```text
frontend/
  src/                 authored ES modules
  test/                executable Vitest tests
  scripts/build.mjs    deterministic esbuild entrypoint
  eslint.config.js     JavaScript correctness rules
  package.json         contributor commands and pinned dependency ranges

physics_playground/
  frontend_assets.py   safe, cached package-resource loader
  static/js/           committed production build artifacts
  canvas/player.py     transitional iframe assembly and payload serialization
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
concatenate browser code into the iframe document. Extraction changes code ownership and build
location only; it must not change payload fields, numerical arrays, units, seeds, or interpolation
semantics.

## Staged migration

1. **Foundation — complete.** Maintain the ES-module workspace, deterministic build, static loader,
   CI checks, runtime Vitest proof, and extracted `PhysicsVisuals` utility.
2. **Leaf utilities.** Extract vectors, experience/context helpers, and animation helpers one at a
   time. Add focused runtime tests before replacing each Python constant.
3. **Scientific assets.** Split the asset library by responsibility while preserving the public
   `PhysicsAssets` compatibility object used by current scenes.
4. **Player runtime.** Move playback state, controls, timestep/display interpolation, DPR handling,
   and lifecycle behavior into modules. Retain payload contract characterization tests and add DOM
   tests only where they provide stable behavioral value.
5. **Scene adapters.** Move simulation-specific scene strings from slice `scene.py` files into
   subject/simulation frontend modules. Python scene modules should then serialize data and request
   named built assets rather than contain editable JavaScript.
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
