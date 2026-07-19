# Physics Studio architecture

## Architectural intent

Physics Studio separates scientific authority from delivery. Physics models own numerical and
analytical meaning. Presentation code turns immutable results into learning modes, charts, and
browser scenes. Streamlit is the current presentation shell; it is replaceable and is not part of
the physics domain.

All 22 simulations use subject-oriented vertical slices with validated direct page loading.
Shared packages provide contracts, rendering infrastructure, persistence, missions, and
presentation helpers; they do not own simulation-specific pages or physics.

## Runtime map

```text
app.py
  -> physics_playground/registry.py
       -> validated manifest and lazy page-entrypoint import
            -> Streamlit page and four learning modes
                 -> pure physics model
                 -> mission evaluator
                 -> notebook/profile adapters
                 -> chart helpers
                 -> canvas document builder
                      -> shared browser player and visual assets
```

Cross-cutting state is provided by:

- slice `metadata.py` modules for mission definitions, with `physics_playground/missions/` providing
  typed models, discovery indexes, pure evaluation services, and Streamlit integration;
- `physics_playground/notebook.py` for UI-independent trial records;
- `physics_playground/profiles.py` for local SQLite/JSON profile persistence;
- `physics_playground/accessibility_settings.py` for UI-independent accessibility preferences;
- `physics_playground/presentation/` for Streamlit-facing adapters and charts.

Canonical shared-module responsibilities are intentionally explicit:

- `accessibility_settings.py` owns framework-neutral preference data;
- `presentation/accessibility_ui.py` owns Streamlit controls and chart accessibility;
- `visual/primitives.py` owns low-level shared Canvas JavaScript;
- `missions/ui.py` owns the active Streamlit mission adapter;
- `canvas/embed.py` owns Streamlit iframe embedding.

The canonical domain name is `LearningMode`. Warning-producing `InteractiveMode` and
`SimulationMode` import shims remain for external compatibility; Kid/Expert are not active product
modes. Cannonball retains only aliases for learner-authored or setup state that may survive a
browser session. Its transient controller aliases have been removed.

## Pure physics-model boundary

Simulation models live in a vertical slice's `physics.py`; shared architecture models remain in
`physics_playground/models/`.
They may depend on contracts, validation, numerical helpers, NumPy, and Python's standard library.
They must not import Streamlit, Matplotlib, presentation modules, or canvas modules.

A model should:

1. accept a typed parameter object;
2. validate ranges, finiteness, and computational budgets;
3. compute deterministic results for identical inputs and seeds;
4. return typed results with explicit units and model metadata;
5. expose assumptions, limitations, warnings, and numerical diagnostics where relevant.

This boundary lets tests call physics without initializing a web application. It also means a
future frontend or service can consume the same results without reimplementing equations.

## Presentation and browser boundary

Pages coordinate the four learning modes and translate model results into text, charts, notebook
records, mission evidence, and rendering payloads. Python canvas adapters serialize precomputed
samples into HTML documents. JavaScript interpolates and draws those samples; it does not own the
physics integration or alter recorded results.

Python player adapters are in `physics_playground/canvas/`. Shared scientific assets and tokens are
under `physics_playground/visual/`. Editable browser code lives as ES modules under `frontend/src/`,
is checked with ESLint, Prettier, and Vitest, and is built into static assets loaded by Python.
Behavioral and representative perceptual tests cover the payload boundary and browser rendering;
manual inspection remains useful for broad appearance review.

## Vertical slices

Simulations live at:

```text
physics_playground/subjects/<subject>/<simulation>/
  __init__.py
  physics.py
  missions.py
  metadata.py     # registry and mission declarations
  lesson.py       # when the simulation anchors authored curriculum
  page.py
  charts.py       # when simulation-specific
  scene.py        # when simulation-specific
```

A subject may share canvas or UI helpers at its package root. A slice should own simulation-specific
physics, mission evidence, and page composition. Reusable rendering, state, chart, or validation
logic belongs in shared modules rather than being copied into slices.

The supported subject identifiers are defined by `SubjectArea` in
`physics_playground/models/expansion.py`.

## Manifests, validation, and registry

Subject `manifests.py` modules create transitional `ExpansionDefinition` records. The combined catalog in
`physics_playground/expansion_catalog.py` covers all 22 simulations. Validation in
`physics_playground/expansion_validation.py` requires:

- complete metadata and stable IDs;
- all four learning modes and their required capabilities;
- typed parameter, result, physics, and page entrypoints;
- at least three missions with matching simulation ownership;
- assumptions and limitations;
- declared physics-invariant and validation-test coverage;
- a prediction capability in Explore mode.

Each slice's `metadata.py` is the metadata source for navigation, cards, missions, and stable IDs.
`physics_playground/registry.py` discovers and validates a unique index of those declarations.
Runtime loading goes through `load_validated_page()`, which requires a manifest, validates it, and
then lazily imports its page entrypoint. Expansion manifests add implementation contracts and
reference discovered metadata. The manifest's pure-physics entrypoint and result name remain
transitional because expansion validation deliberately checks the `physics.py` boundary.

## Product and package names

The product name is **Physics Studio**. The import package remains `physics_playground` because a
repository-wide rename would break imports, persisted references, packaging, and downstream users
without improving the current course architecture. This is deliberate technical debt. A future
rename requires a separately approved compatibility plan, an import shim and release window, and
evidence that persisted entrypoint strings have migrated.

Model versions are owned by each slice's pure physics module. Metadata imports that constant;
notebook records derive it from metadata. Presentation pages do not declare versions.

## Discovery and navigation

The home screen is the primary discovery surface. `presentation/navigation.py` joins subject
ownership from validated expansion manifests with units and lessons from the curriculum manifest.
It does not maintain a separate simulation taxonomy. Searchable home cards expose lessons,
simulations, concepts, difficulty, and learner progress.

The sidebar intentionally stays bounded as the catalog grows: it contains subject,
unit-or-collection, and concept selectors, but never one control per simulation. An unfinished
lesson may be recommended as an optional next activity; recommendations do not hide or gate other
content. Native Streamlit controls retain keyboard behavior and the shared responsive CSS wraps
controls on narrow screens.

Simulation registry IDs remain the stable navigation identifier. Links may use
`?simulation=<registry-id>` and optionally `&lesson=<curriculum-lesson-id>`. URL targets are
validated against the registry and curriculum before use.

## Compatibility and state

Stable simulation IDs, mission IDs, model versions, notebook fields, and profile schemas are
compatibility surfaces. Streamlit session-state keys are also observable during a session. Change
them only with explicit data migrations where appropriate.

The current architecture migration plan is documented in
`docs/ARCHITECTURE_MIGRATION.md`. It favors one runnable, testable stage at a time and does not
authorize changing physics during file moves.

The completed review-to-current-state assessment, remaining debt, readiness verdicts, and revised
grades are recorded in `docs/PRINCIPAL_ARCHITECT_AUDIT.md`.

## Tests and quality gates

The complete local gate is:

```bash
ruff format --check .
ruff check .
mypy
pytest
python -m build
```

`tests/test_architecture_dependencies.py` is the reproducible dependency and import-cycle gate. It
enforces semantic boundaries for physics, the registry, and education contracts rather than
arbitrary directory shapes.

MyPy currently checks a documented ratchet of typed foundation modules. See
`docs/DEVELOPMENT.md` for how to expand that boundary.

Real-browser accessibility evidence, known Streamlit limitations, and the manual assistive-
technology release checklist are maintained in `docs/ACCESSIBILITY_VERIFICATION.md`.

## Shared physical constants

`physics_playground.units` is the canonical home for shared physical assumptions. Names include
units (`EARTH_GRAVITY_M_S2`, `STANDARD_ATMOSPHERE_PA`) and values are documented in SI units.
Import a constant when multiple simulations mean the same assumption; retain a model parameter
when learners can configure it. Similar numbers are not automatically the same physical concept.
Frontend-only defensive fallbacks may repeat a value when Python cannot supply it.

## Streamlit session state

`physics_playground.state_keys` owns the small set of cross-cutting keys. Navigation,
accessibility, profiles, missions, and notebook state use `SHARED_STATE_KEYS`. New feature state
uses `feature_key(feature, name)` and vertical slices use
`simulation_key(simulation_id, name)`. The `physics_studio.*` namespace avoids collisions without
introducing a state manager. `migrate_legacy_keys` preserves sessions created before namespacing.

## Application callbacks

`physics_playground.application_callbacks` is the explicit seam between learning-state changes
and Streamlit integration. Missions emit typed badge and progress events; notebook and
accessibility UI emit their corresponding typed changes. `app.py` connects those events to local
profile persistence and supplies player preferences. Domain services never import Streamlit UI,
and callback failures propagate instead of being silently discarded. This is intentionally one
synchronous callback and one player-preference provider, not a general event framework.
