# Physics Studio architecture migration audit

Date: 2026-07-18
Repository baseline: current working tree at audit time

## Migration progress

Stage 3 is underway. Two dependency-ordered waves have been completed after the audit:

- **Completed:** `cannonball` moved to `subjects/mechanics/cannonball/`.
- **Completed:** `pendulum` moved to `subjects/waves_and_oscillations/pendulum/`.
- **Completed:** `orbital_gravity` moved to `subjects/mechanics/orbital_gravity/`.
- **Completed:** `boing` moved to `subjects/waves_and_oscillations/boing/`.
- **Remaining horizontal simulations, in planned order:** `earth_tunnel`, `double_pendulum`, and
  `bumper_cars`.

Each completed slice owns `physics.py`, `page.py`, `missions.py`, `charts.py`, and `scene.py`, is
enrolled in the expansion manifest catalog, is loaded through registry manifest validation, and
uses namespaced simulation state with compatibility migration reads. The inventory and counts
below describe the original audit baseline and are retained as historical evidence.

## Scope and evidence

This document is based on a repository-wide inspection of `app.py`, all Python packages under `physics_playground/`, all tests, packaging configuration, current Markdown documentation, and the supplied Principal Architect Review. The review describes an earlier repository state in several places, so every factual claim was checked against the current tree rather than accepted as a premise. Subjective grades and strategic opinions are identified as judgments rather than repository facts.

No application code was changed during this audit. This file is the only intended modification.

## Executive assessment

Physics Studio is a runnable registry-driven Streamlit monolith with a strong shared model/rendering foundation but two coexisting simulation layouts:

- seven older simulations use a horizontal package split across `models/`, `pages/`, `canvas/`, `missions/`, and `presentation/`;
- fifteen newer simulations use subject-oriented vertical slices under `subjects/<subject>/<simulation>/` while still depending on shared top-level rendering and presentation infrastructure.

The application has already resolved several likely historical concerns: all 22 simulations are registry enrolled, expose four learning modes, use the shared browser player, use structured missions, and participate in the notebook/profile system. The largest remaining architectural inconsistency is not the physics engine; it is ownership. Simulation metadata, model metadata, mission definitions, bindings, page code, state keys, presets, and constants are distributed across multiple catalogs with incomplete coverage.

## Finding classification

| Classification | Current repository-backed finding |
|---|---|
| **Confirmed** | Two simulation architectures coexist: 7 horizontal and 15 vertical-slice simulations. |
| **Confirmed** | `SIMULATION_REGISTRY` is the navigation source of truth, but mission definitions, model metadata, expansion manifests, and reusable bindings are separate catalogs. |
| **Confirmed** | Only Cannonball has a `SimulationBinding`; the reusable binding/preset architecture covers 1 of 22 simulations. |
| **Confirmed** | Session state is decentralized: static analysis found at least 131 literal widget/session keys, mostly declared inline in pages. |
| **Confirmed** | Physical presets/constants are duplicated despite `physics_playground/units.py`; `9.81` occurs 42 times across 15 package files, `1.62` 10 times, Earth-radius literals 9 times, `343` 3 times, and `101325` 4 times in package code. |
| **Confirmed** | Broad exception suppression exists at persistence boundaries and one analytical chart path; details are inventoried below. |
| **Confirmed** | Public-function typing is inconsistent: a conservative top-level AST scan found 248 public functions across 70 modules with at least one missing argument or return annotation. |
| **Confirmed** | README references `EXPANSION_ARCHITECTURE.md` and `upload/`, neither of which exists. Several historical counts and migration statements are stale. |
| **Already resolved** | All 22 registered simulations use the shared JavaScript player and shared visual vocabulary; no simulation owns a separate animation loop. |
| **Already resolved** | Explore, Compare, Analyze, and Model are declared for every registry item. |
| **Already resolved** | Typed parameter/result models, deterministic tests, structured mission evidence, notebook capture, local profiles, accessibility preferences, and responsive rendering exist and are tested. |
| **Already resolved** | The old standalone HTML generator is gone. `canvas/embed.py` is the canonical one-function iframe adapter, and `canvas/legacy.py` is a compatibility re-export. |
| **Already resolved** | Contrary to the review, the repository now has an installable `pyproject.toml` and a `.python-version` file. |
| **Partially resolved** | Vertical-slice manifests cover the 15 subject simulations, but the registry and mission catalog still live centrally and canvas ownership is often shared by family rather than slice. |
| **Partially resolved** | Model metadata covers 22 simulations, but page-level assumptions and defaults are still duplicated and can diverge. |
| **Partially resolved** | Setup reuse has a typed `SimulationSetupRequest`, but only Cannonball consumes it at runtime and bindings exist only for Cannonball. |
| **Partially resolved** | Profile persistence is typed and versioned, but it serializes a loosely typed notebook payload and does not persist visual presentation/theme preferences alongside the three accessibility booleans. |
| **No longer applicable** | Claims that the app has seven simulations, only 25 missions, only an initial pilot renderer set, or an unfinished visual migration are obsolete. Current counts are 22 simulations and 85 mission definitions. |
| **Newly discovered** | The README says the free-fall example is outside a seven-item registry and refers to original uploaded files; both statements are stale in the current 22-simulation repository. |
| **Newly discovered** | `presentation/formatting.py` and `units.py` have no production or test consumers even though equivalent formatting and constants are duplicated elsewhere. |
| **Newly discovered** | `binding_catalog.py` is a production-quality architecture with tests but is effectively a one-simulation pilot, creating a second incomplete catalog beside expansion manifests. |

## Principal Architect Review claim verification

The table below covers the review's material, repository-testable assertions. Product judgments such as letter grades, “wrong endgame,” “disqualifying,” or the claim that “almost everything” must be rebuilt are not facts that can be verified from source. The evidence supports incremental consolidation; it does not establish a need for a wholesale rewrite.

| Review claim | Current evidence | Classification |
|---|---|---|
| Seven simulations are horizontal and fifteen are vertical slices. | Registry-to-module inventory yields exactly 7 and 15; both inventories follow below. | **Confirmed** |
| `EXPANSION_ARCHITECTURE.md` and `upload/` do not exist. | Both are absent but still referenced by README. | **Confirmed** |
| `.python-version` does not exist. | `.python-version` exists. | **Already resolved** |
| `pyproject.toml` does not exist and the package is not installable. | A setuptools `pyproject.toml` exists with project metadata, package discovery, runtime dependencies, pytest config, and a test extra. | **Already resolved** |
| There is no LICENSE, CONTRIBUTING guide, formatter/linter/type config, pre-commit, or CI workflow. | None is present; `pyproject.toml` configures packaging and pytest only. | **Confirmed** |
| The binding registry contains exactly one simulation. | `binding_catalog.py` contains the Cannonball binding only. | **Confirmed** |
| `units.py` is imported only by tests. | It has no production or test import. It is more unused than the review states. | **Partially resolved** |
| `integrators.py` is imported only by tests. | `tests/test_foundation.py` imports `rk4_step`; package code does not. | **Confirmed** |
| `examples/free_fall.py` is used by nothing. | It is exported and exercised by contract/foundation tests, but is not registry-enrolled runtime functionality. | **Partially resolved** |
| `setup_handoff.py` is consumed in one runtime place. | Notebook UI produces requests and only Cannonball consumes them; tests also exercise it. | **Confirmed** |
| `9.81` appears in 34 files. | It currently appears 42 times across 15 package files, not 34 files. Duplication remains material. | **Partially resolved** |
| Pure physics modules do not depend on Streamlit/rendering. | Import inspection confirms the domain/UI dependency boundary. | **Confirmed** |
| Mission, accessibility, player, and profile integration use lazy imports and broad suppression to break cycles. | Broad suppression exists at the persistence seams and player preference fallback. The exact issue is runtime coupling through session/profile persistence, not one single Python import cycle proven by tooling. | **Partially resolved** |
| Rendering JavaScript lives inside Python strings and is tested structurally. | The six named shared JS bundles and scene scripts are Python strings concatenated into iframe HTML. Tests include substring and hash assertions; no JS runner is configured. | **Confirmed** |
| No JS linting, formatting, source maps, runtime unit tests, or bundler exists. | No JS project/toolchain configuration exists. | **Confirmed** |
| Naming is ambiguous (`accessibility` twice, `simulation_binding[s]`, canvas package/module, live `missions/legacy.py`). | Responsibility-based canonical modules now own each implementation; old paths are compatibility re-exports only. | **Already resolved** |
| Session keys are ad hoc and unnamespaced. | Static analysis finds at least 131 literal widget/session keys with page-local prefixes. | **Confirmed** |
| Registry is the single source for navigation and page loading. | `app.py` and home/navigation resolve through `SIMULATION_REGISTRY` with lazy page imports. | **Confirmed** |
| Expansion manifests gate registry entry. | Manifests are validated by tests/catalog integration, but the runtime registry is still separately declared rather than generated from them. | **Partially resolved** |
| Four modes and prediction-before-experiment are consistently present. | All 22 registry definitions declare the four modes; prediction helpers are used across pages. | **Confirmed** |
| No lesson, curriculum, course-sequencing, or cross-simulation progression model exists. | No such domain model or catalog is present; prerequisites are mission-local. | **Confirmed** |
| The product voice mixes child-oriented language with advanced analysis. | README says “kid-friendly”; balloon celebrations, recess/brushing-teeth copy, and advanced phase-space/model views coexist. | **Confirmed** |
| Returning learners must re-answer prediction gates because reveal state is never persisted. | Reveal state is held in Streamlit session state, not profiles. It survives same-session reruns but not a new profile session. | **Partially resolved** |
| Inclined-plane force vectors use a nonlinear normalized mapping without quantitative scale. | Scene code uses normalized visibility mapping and the shared vector-semantics disclosure architecture; it is not physically proportional. Current structural tests enforce semantics, not learner comprehension. | **Partially resolved** |
| Sidebar navigation is a flat 22-item radio list. | `app.py` builds a registry-wide sidebar selection rather than a subject tree. | **Confirmed** |
| Streamlit reruns can remount players and lose playback state. | Player state is iframe-local and no persistence bridge exists across a remount. Exact perceived jank was not browser-profiled. | **Partially resolved** |
| Accessibility support includes reduced motion, high contrast, large text, keyboard control, ARIA status, focus rings, and non-color line distinctions. | These mechanisms exist in settings, CSS, player JS, and chart styling. There are structural tests but no browser accessibility test suite. | **Confirmed** |
| High contrast depends on `!important` selectors over Streamlit DOM. | Shared accessibility CSS contains `!important` overrides. Upgrade fragility is a reasonable risk, not a measured failure. | **Confirmed** |
| Static Matplotlib charts are regenerated on rerun and Analyze scans are uncached. | Matplotlib is the shared chart path; several page-level scan loops are outside cached model entrypoints. No runtime profile quantifies the cost. | **Partially resolved** |
| Newer code is heavily compressed and contains extreme line lengths. | Static scan finds 74 lines longer than 500 characters across 26 Python files; formatting is materially inconsistent. | **Confirmed** |
| Bumper Cars shadows the model import with a cached function import. | Consecutive imports bind both functions to `simulate_collision`; the latter wins. | **Confirmed** |
| README references two nonexistent focused test files. | Both referenced paths are absent; related consolidated tests exist under different names. | **Confirmed** |
| Magic seeds are scattered inline. | Numerous page calls pass literal deterministic seeds; no shared seed catalog or naming convention exists. | **Confirmed** |
| 442 tests pass in roughly five seconds. | Current baseline is 442 passed, 6.34 s pytest time and 6.94 s wall time. Count is current; timing differs by machine/run. | **Partially resolved** |
| Visual tests are mainly string/hash change detectors and there are no browser goldens. | Such assertions exist, including wave migration token checks and a SHA-256 asset assertion. There are also meaningful geometry/configuration tests, so “mainly” is too broad without weighting tests. No browser/pixel suite exists. | **Partially resolved** |
| Streamlit `AppTest` is unused and there is no CI. | No `AppTest` reference and no workflow files exist. | **Confirmed** |
| Player uses requestAnimationFrame, DPR sizing, visibility pausing, and teardown. | Shared player/animation code contains these lifecycle mechanisms and structural tests cover them. | **Confirmed** |
| Every iframe embeds and reparses the concatenated JS bundle. | `build_player_document()` inlines all shared bundles plus scene JS into each generated document. Browser parse cost was not profiled. | **Confirmed** |
| Local profiles use SQLite/JSON and there is no authentication or multi-user identity service. | `ProfileStore` is local SQLite with JSON payloads; no auth/remote identity layer exists. | **Confirmed** |
| Saved notebooks and badges are mature roadmap features. | Both have typed models/services, persistence integration, export/UI paths, and tests. “Mature” is evaluative, but the implementation claim is confirmed. | **Confirmed** |
| All rendering/presentation above the physics layer must be rebuilt. | Current shared player, assets, vectors, design tokens, accessibility, charts, missions, notebook, and profiles are active and tested. Targeted extraction/consolidation is warranted; wholesale replacement is unsupported. | **No longer applicable** |

## 1. Current architecture map

```text
app.py
  ├─ registry.py ──> dynamic import of each SimulationDefinition.page_module
  ├─ presentation/home.py
  ├─ presentation/profile_ui.py ──> profiles.py (SQLite/JSON)
  ├─ presentation/accessibility_ui.py ──> accessibility_settings.py + visual/*
  ├─ presentation/notebook_ui.py ──> notebook.py + setup_handoff.py
  └─ missions/ui.py ──> missions/service.py + missions/definitions.py

simulation page
  ├─ parameter widgets / mode orchestration / session keys
  ├─ pure physics model
  ├─ simulation mission evaluator ──> MissionEvaluation[]
  ├─ notebook_ui.add_trial()
  ├─ shared chart renderer
  └─ canvas family adapter
       └─ canvas/player.py
            ├─ visual/tokens.py + visual/css.py
            ├─ visual/assets.py
            ├─ visual/vectors.py
            ├─ visual/animation.py
            └─ visual/experience.py

parallel catalogs
  ├─ registry.py                         22 navigation definitions
  ├─ model_metadata.py                   22 model metadata records
  ├─ missions/definitions.py             85 centralized mission definitions
  ├─ expansion_catalog.py + manifests    15 vertical-slice definitions
  └─ binding_catalog.py              1 reusable binding and preset
```

### Runtime boundaries

- **Pure/domain layer:** most files in `models/`, slice `physics.py` modules, `contracts.py`, `notebook.py`, `history.py`, `binding_models.py`, validation, units, and integrators.
- **Application/presentation layer:** `app.py`, all page modules, `presentation/*`, `missions/ui.py`, and Streamlit session state.
- **Browser rendering boundary:** Python serializes immutable results into a complete HTML document; JavaScript interpolates display samples but does not run physics models.
- **Persistence boundary:** `ProfileStore` stores one JSON profile payload per SQLite row; the profile embeds notebook data, mission IDs, accessibility settings, and recent parameters.

## 2. Legacy horizontal simulation inventory

These seven simulations are organized by technical layer rather than simulation ownership.

| Simulation ID | Model | Page | Canvas | Mission evaluator | Chart/presentation helpers |
|---|---|---|---|---|---|
| `cannonball` | `models/projectile.py` | `pages/cannonball.py` | `canvas/cannonball.py` | `missions/cannonball.py` | `presentation/projectile_charts.py` |
| `pendulum` | `models/pendulum.py` | `pages/pendulum.py` | `canvas/pendulum.py` | `missions/pendulum.py` | `presentation/pendulum_charts.py` |
| `orbital_gravity` | `models/orbit.py` | `pages/orbital_gravity.py` | `canvas/orbit.py` | `missions/orbit.py` | `presentation/orbit_charts.py` |
| `bumper_cars` | `models/collision.py` | `pages/bumper_cars.py` | `canvas/bumper_cars.py` | `missions/bumper_cars.py` | `presentation/bumper_cars.py`, `bumper_learning.py` |
| `boing` | `models/spring.py` | `pages/boing.py` | `canvas/boing.py` | `missions/boing.py` | `presentation/spring_charts.py` |
| `double_pendulum` | `models/double_pendulum.py` | `pages/double_pendulum.py` | `canvas/double_pendulum.py` | `missions/double_pendulum.py` | `presentation/double_pendulum_charts.py` |
| `earth_tunnel` | `models/earth_tunnel.py` | `pages/earth_tunnel.py` | `canvas/earth_tunnel.py` | `missions/earth_tunnel.py` | `presentation/tunnel_charts.py` |

“Legacy horizontal” describes file ownership only. These simulations are not legacy in rendering or user experience: all seven use typed models, the shared player, four modes, missions, notebook integration, and current visual infrastructure.

## 3. Vertical-slice simulation inventory

These fifteen simulations colocate `physics.py`, `page.py`, `missions.py`, and package exports under a subject hierarchy.

| Subject | Simulation IDs | Shared canvas ownership |
|---|---|---|
| Mechanics | `inclined_plane`, `torque_levers`, `center_of_mass`, `roller_coaster`, `rotational_motion` | `subjects/mechanics/canvas.py` |
| Waves and oscillations | `wave_interference`, `doppler_effect` | `canvas/scalar_field.py`, `canvas/wavefronts.py` |
| Light and electricity | `reflection_refraction`, `thin_lenses`, `electric_fields`, `magnetic_forces` | `canvas/ray_diagram.py`, `vector_field.py`, `vector_diagram.py` |
| Fluids and matter | `buoyancy`, `fluid_pressure`, `gas_laws`, `diffusion` | `canvas/fluid_container.py`, `gas_container.py`, `diffusion_player.py` |

Each subject also owns a `manifests.py`; `expansion_catalog.py` aggregates all 15. These slices still depend on centralized registry entries and centralized mission definitions, so the vertical architecture is only partial.

## 4. Dependency maps

### Missions

```text
missions/definitions.py (85 MissionDefinition records)
  ├─ MISSIONS_BY_SIMULATION
  ├─ missions/service.py (pure MissionProgress and evaluate_run)
  ├─ missions/ui.py (Streamlit compatibility/UI/state)
  ├─ per-simulation evaluator modules (pure MissionEvaluation evidence)
  └─ subject manifests (copy mission tuples into ExpansionDefinition)

page Run button
  -> evaluator(result)
  -> missions/legacy.process_run()
  -> service.evaluate_run()
  -> st.session_state.mission_progress / missions
  -> profile_ui.persist_active_session()
```

The pure service boundary is good. The main coupling is that all mission metadata remains in one large central file while evidence evaluators are split between horizontal and vertical locations.

### Profiles

```text
presentation/profile_ui.py
  -> profiles.ProfileStore
       -> SQLite profile table (JSON payload, schema version 2)
  -> MissionProgress
  -> ExperimentNotebook
  -> AccessibilitySettings
  -> registry navigation/favorite IDs

app.py -> render_profile_sidebar() at start
app.py -> persist_active_session() after every render
mission/notebook actions -> best-effort persist_active_session()
```

Failure to open the database intentionally degrades to session-only mode. Save failures are surfaced through `persistence_error`, but several callers suppress persistence exceptions entirely.

### Accessibility

```text
accessibility_settings.py
  -> AccessibilitySettings(reduced_motion, high_contrast, large_text)

presentation/accessibility_ui.py
  -> Streamlit widgets/session keys
  -> global CSS and Matplotlib line/color/marker cycle
  -> VisualPreferences(presentation level, theme)

canvas/player.py
  -> reads settings/preferences during document build
  -> serializes reducedMotion, highContrast, largeText, theme, presentationLevel
  -> browser player honors OS reduced motion and theme
```

Accessibility booleans persist in profiles. Visual theme and presentation level currently remain session preferences and are not included in `LocalProfile`.

### Notebook state and setup reuse

```text
st.session_state["experiment_notebook"]
  -> ExperimentNotebook
       -> TrialRecord[] (parameters, metrics, seed, model version, observations)
       -> pin/compare/delete/reset/export

presentation/notebook_ui.py
  -> add_trial()
  -> report builder
  -> setup_handoff.queue_setup_request()

st.session_state["notebook_reuse_request"]
  -> typed SimulationSetupRequest serialized as dict
  -> consumed by individual pages
```

Notebook storage is UI-independent and bounded. Rehydration into controls is page-specific, which is one motivation for completing `SimulationBinding` coverage.

### JavaScript rendering

```text
model result / AnimationData / simulation geometry
  -> family build_*_document()
  -> canvas/player.build_player_document()
       -> JSON payload
       -> PLAYER_JS requestAnimationFrame lifecycle
       -> shared token/theme payload
       -> PhysicsAssets / PhysicsAnnotations / PhysicsAnimation / PhysicsExperience
  -> canvas/embed.show()
  -> Streamlit iframe
```

All simulation adapters use the shared player. `canvas/embed.py` is the active one-function iframe adapter; `canvas/legacy.py` is a compatibility re-export.

## 5. Technical-debt inventory

### Dead or speculative modules

| Module | Status | Evidence and disposition |
|---|---|---|
| `presentation/formatting.py` | **Confirmed dead candidate** | No production or test imports. Duplicates `missions/ui.py` friendly speed/time helpers. Deprecate only after deciding the canonical formatting API. |
| `units.py` | **Confirmed unused candidate** | Defines useful gravity/unit constants but has no imports; callers duplicate the constants. Adopt it first, then keep it as canonical rather than deleting it. |
| `examples/free_fall.py` | **Intentional speculative example** | Exported by `examples/__init__.py` and exercised by contract tests; not registry enrolled. Keep as contract documentation or replace with a real slice fixture later. |
| `history.py` | **Test/example-only abstraction** | Used by contract tests, not the running app; overlaps `ExperimentNotebook`. Decide whether generic contract history or notebook is canonical. |
| `binding_catalog.py` | **Partial production pilot** | Strongly tested but contains only Cannonball. Expand to 22 or explicitly scope it to lessons/presets. |
| `models/expansion.py`, manifests, `expansion_catalog.py` | **Active architecture scaffold** | Used by validation and cross-simulation tests for 15 slices, but not runtime navigation. Not dead; consolidate with the registry rather than removing. |
| `canvas/legacy.py` | **Compatibility surface** | Re-exports `canvas.embed.show()` for downstream imports; internal consumers use the canonical module. |

Dynamic registry page imports make simple static “zero inbound import” reports unreliable for page modules; pages are active even when no static import points to them.

### Hardcoded physical constants

- Gravity presets are duplicated across model defaults, pages, comparisons, missions, examples, and JavaScript fallbacks. `units.py` already defines Earth/Moon/Jupiter values but is unused.
- Planet radii and gravities are repeated in `pages/earth_tunnel.py` and tunnel missions.
- Sound speed `343 m/s` and default `440 Hz` appear in both Doppler model and page controls.
- Standard atmospheric pressure `101325 Pa` appears in fluid-pressure defaults/pages/tests without a named package constant.
- `inclined_plane/page.py` calculates display weight using literal `9.81` rather than `r.parameters.gravity_m_s2`, creating a real divergence risk if gravity becomes configurable.
- `subjects/mechanics/canvas.py` has a `9.81` JavaScript fallback. This is acceptable as defensive rendering but should be named or supplied explicitly.

Defaults in typed parameter models are legitimate. The migration target is one canonical preset catalog, not elimination of every numeric literal.

### Silent exception handling

| Location | Behavior | Risk |
|---|---|---|
| `missions/ui.py::process_run` | Broad `except Exception: pass` around profile persistence | Mission succeeds but persistence failure can be invisible. |
| `presentation/notebook_ui.py::add_trial` | Broad `except Exception: pass` around profile persistence | Trial exists in session but may not persist, without local feedback. |
| `presentation/accessibility_ui.py::render_accessibility_panel` | Broad inline suppression around profile persistence | Preference persistence may fail silently. |
| `canvas/player.py::build_player_document` | Broad exception fallback when reading Streamlit preferences | Intentional framework-neutral fallback, but catches programming errors as well as missing runtime context. |
| `electric_fields/page.py::analyze` | Broad exception converts field probes to `None` | Produces chart gaps without recording which numerical/validation error occurred. |

`profile_ui.persist_active_session()` itself catches expected save errors and records `persistence_error`; callers should use that result rather than catching every exception.

### Untyped public functions

A conservative AST scan of module-level public functions found 248 functions across 70 modules with a missing parameter annotation or missing return annotation. This does not mean the domain model is untyped: core contracts and many dataclasses are typed. The concentration is in:

- Streamlit page `render/explore/compare/analyze/model/controls` functions;
- canvas document builders;
- mission evaluator helpers;
- cache wrappers and presentation helpers;
- profile store/UI methods and manifest factories.

Prioritize reusable/public boundaries (`build_*`, `evaluate`, persistence, serialization, cache decorators, manifest factories) before annotating internal Streamlit render functions.

### Ad hoc session-state keys

Static analysis found at least 131 literal Streamlit widget or session keys. Key ownership is partly centralized for profiles, notebook, accessibility, and setup handoff, but simulation pages mostly build keys ad hoc (`pend_*`, `chaos_*`, `coaster_*`, etc.). Risks include typo-only migrations, incomplete profile restoration, and collision during slice moves.

Recommended structure:

```text
SessionKeys
  core.navigation
  accessibility.*
  profile.*
  notebook.*
  simulation.<simulation_id>.<mode|control|run_state|observation>
```

Introduce aliases and migration reads before changing existing keys; notebook restoration and saved profiles depend on current names.

### Documentation references and stale claims

- `README.md` links to nonexistent `EXPANSION_ARCHITECTURE.md`.
- `README.md` says original files remain in nonexistent `upload/`.
- The free-fall section says it is outside a seven-item registry; the registry contains 22 simulations.
- The README refers to “all 25 original achievements”; there are currently 85 mission definitions.
- It describes an initial pilot set and “remaining adapters” even though the visual migration is complete.
- It calls Bumper Cars the first/reference migration. Historically useful, but no longer a current architecture description.
- `docs/VISUAL_SYSTEM.md` exists and accurately documents the completed shared visual system.

## 6. Test and tooling baseline

Commands were run from the repository root with `.venv/bin/python`.

| Check | Result |
|---|---|
| Python tests collected | **442** |
| Python tests passed | **442 passed** |
| Pytest reported runtime | **6.34 s** |
| End-to-end command wall time | **6.94 s** |
| Maximum resident set during test command | **139,388 KB** |
| Collection-only runtime | **2.39 s** |
| Bytecode compilation | `python -m compileall -q app.py physics_playground tests` passed |
| Coverage | Not configured; `coverage`/`pytest-cov` are not installed, so no percentage is claimed |
| Formatting | No formatter configured; Black and Ruff are not installed, so formatting status is **unknown**, not passing |
| Lint | No lint configuration or installed Ruff executable; lint status is **unknown** |
| Type checking | No MyPy/Pyright configuration or installed executable; type-check status is **not established** |

`pyproject.toml` makes the package installable and configures setuptools and pytest. Its `test` extra includes pytest, but neither it nor `requirements.txt` provides quality or coverage tooling.

## 7. Staged migration plan

Every stage below is designed to leave `streamlit run app.py` runnable and the full suite green. Avoid moving physics and changing behavior in the same stage.

### Stage 0 — freeze observable contracts

1. Add an architecture-contract test that snapshots registry IDs, page entrypoints, model versions, mission ownership, notebook/profile schema versions, and legacy public imports.
2. Add characterization tests for setup reuse and saved profile/notebook payloads for all seven horizontal simulations.
3. Add test/lint/type dependencies in an optional `dev` extra without initially enforcing new failures.
4. Capture a coverage baseline before setting a threshold.

Exit condition: no runtime changes; current public paths and serialized state are protected.

### Stage 1 — establish one canonical simulation descriptor

1. Extend `SimulationDefinition` or introduce a composed `SimulationDescriptor` containing registry metadata plus typed parameter/result/runner/page/canvas/mission/model-metadata references.
2. Generate compatibility views for `SIMULATION_REGISTRY`, `MODEL_METADATA`, `EXPANSION_MANIFESTS`, and binding lookup rather than rewriting consumers immediately.
3. Enroll one existing vertical slice and Cannonball as equivalence tests.

Exit condition: old catalogs still import and return identical values; navigation remains registry driven.

### Stage 2 — complete binding and setup-reuse coverage

1. Add `SimulationBinding` entries incrementally for all simulations, one subject family per change.
2. Move parameter deserialization and validation behind bindings.
3. Let pages consume typed `SimulationSetupRequest` through a shared helper while retaining old session-key aliases.
4. Add presets only where real educational content needs them; do not create speculative presets merely for coverage.

Exit condition: every simulation can restore a typed notebook setup without page-specific raw dictionary parsing.

### Stage 3 — migrate the seven horizontal simulations into vertical slices

Migrate one simulation at a time in this order:

1. Cannonball — **completed**
2. Pendulum — **completed**
3. Orbit — **completed**
4. Boing — **completed**
5. Earth Tunnel — remaining
6. Double Pendulum — remaining
7. Bumper Cars — remaining

For each simulation:

1. Create `subjects/<subject>/<simulation>/` with `physics.py`, `page.py`, `missions.py`, and optional `canvas.py`/`charts.py` only when ownership is simulation-specific.
2. Move or re-export the existing implementation without changing model equations or arrays.
3. Keep forwarding modules at the old `models.*`, `pages.*`, `missions.*`, and `canvas.*` paths.
4. Change the registry page entrypoint only after equivalence tests pass.
5. Remove a forwarding module only in a separately approved deprecation release.

Exit condition per slice: old and new imports produce identical parameter/result types, notebook records, mission evidence, and player payloads.

### Stage 4 — centralize constants and state-key ownership

1. Adopt `units.py` as the canonical physical preset module and add planet/acoustics/atmosphere presets with explicit units and provenance comments.
2. Replace display-layer literals first; then model defaults where doing so does not alter constructor signatures or serialized defaults.
3. Introduce namespaced session-key factories and compatibility aliases.
4. Migrate one page family at a time; preserve reads of legacy keys for existing sessions and profile imports.

Exit condition: duplicated presets are removed without changing default numerical results or saved-state restoration.

### Stage 5 — clarify persistence and error boundaries

1. Replace broad persistence suppression with a typed best-effort result or narrow exception set.
2. Surface one non-disruptive persistence warning per session instead of failing scientific runs.
3. Narrow the player preference fallback to expected missing-Streamlit-context errors.
4. Record electric-field analysis exclusions with a typed reason rather than swallowing arbitrary exceptions.
5. Decide whether visual theme/presentation level should join profile schema version 3; supply a migration if yes.

Exit condition: expected degraded behavior remains available, unexpected programming errors are observable, and profile schema migration tests pass.

### Stage 6 — extract and behavior-test browser rendering

1. First add browser-level characterization tests for player lifecycle, keyboard control, reduced motion, theme switching, DPR sizing, and representative scene geometry.
2. Move one shared JS bundle at a time from Python constants into real `.js` source files loaded as package resources; preserve the generated iframe document and Python builder interfaces.
3. Introduce a minimal JS formatter/linter/test runner. A bundler is optional: plain modules are sufficient if package-resource loading and deployment remain reliable.
4. Keep scene payload construction in Python and physics execution unchanged.
5. Replace substring/hash assertions only after an equivalent behavior or deterministic-geometry test exists; retain useful structural contract tests.

Exit condition: each extraction produces equivalent player payloads and visible behavior, Python tests remain green, JS checks run independently, and the Streamlit deployment still works without a separate development server.

### Stage 7 — typing, formatting, packaging, and CI gates

1. Annotate public reusable boundaries first, beginning with builders, evaluators, persistence, serialization, cache, and descriptor factories.
2. Configure Ruff for lint/format and MyPy or Pyright with a permissive initial scope. Format mechanical changes separately from functional changes.
3. Enforce checks first on pure/domain and newly migrated vertical-slice modules; ratchet coverage rather than attempting a repository-wide strict switch.
4. Add CI commands matching local documented commands, a coverage baseline, and install/build verification for `pyproject.toml`.
5. Add an explicit LICENSE, CONTRIBUTING guide, and optional pre-commit configuration after the project owner chooses licensing and contribution policy.

Exit condition: tests, format, lint, and scoped type checks run reproducibly in CI.

### Stage 8 — scalable navigation and educational extension seams

1. Replace the flat sidebar list with subject-grouped navigation while preserving stable simulation IDs and deep/session navigation behavior.
2. Introduce typed, initially minimal curriculum structures for sequences, lesson sections, worked examples, and cross-simulation prerequisites. Do not bury lesson content inside page render functions.
3. Decide the primary audience and voice, or introduce an explicit audience/content-depth preference separate from visual presentation level.
4. Persist prediction completion only when pedagogically appropriate; distinguish “attempt again” from involuntary repetition after a new session.
5. Add misconception/limiting-case content through shared typed educational models, beginning with one pilot before broad enrollment.

Exit condition: the current flat discovery experience remains available as a fallback, existing missions/badges are unchanged, and an empty or pilot curriculum cannot block direct simulation access.

### Stage 9 — remove proven duplication and repair documentation

1. Choose between `TrialHistory` and `ExperimentNotebook` for each intended use; document or consolidate without breaking imports.
2. Merge or deprecate `presentation/formatting.py` after moving callers to the chosen shared API.
3. Update README counts and remove references to `EXPANSION_ARCHITECTURE.md`, `upload/`, the seven-item registry, and unfinished visual migrations—or create the missing architecture document if it remains desired.
4. Retain the `canvas/legacy.py` re-export through a documented compatibility window; use `canvas/embed.py` internally.

Exit condition: documentation describes the architecture that actually runs, and removal candidates have zero production, test, dynamic, and documented consumers.

## Migration invariants

Every stage must preserve:

- all existing physics outputs, arrays, units, deterministic seeds, and model-version identifiers;
- all 22 stable simulation IDs and registry navigation labels;
- Explore, Compare, Analyze, and Model behavior;
- mission IDs, prerequisites, hidden status, and earned profile badges;
- notebook JSON/CSV fields, trial numbering, setup reuse, and report inputs;
- profile import/export and SQLite migration behavior;
- shared-player controls, accessibility preferences, and public compatibility imports;
- a passing complete test suite before the next stage begins.
