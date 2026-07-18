# ADR 001: Simulation plugins and a shared learning runtime

- **Status:** Accepted for staged implementation
- **Date:** 2026-07-18
- **Scope:** Architecture and migration boundaries; no runtime implementation is authorized by
  this ADR alone

## Context

Physics Studio has 22 scientifically tested simulations, all in subject-owned vertical slices and
all using the shared browser player. The physics boundary is sound, but Streamlit pages repeat
parameter state, mode dispatch, execution, error handling, notebook recording, missions, and
progress orchestration. The curriculum model is capable, yet only one complete lesson pathway
exists. Profiles and notebooks are local, and only Cannonball uses the browser-native chart
contract.

The immediate goal is one excellent Mechanics course without rewriting the simulations or
committing prematurely to accounts, classroom administration, distributed services, or a frontend
framework. Streamlit remains the delivery shell while the application boundary becomes usable by a
future first-class web frontend.

## Decision

Adopt a composed, immutable `SimulationPlugin` descriptor and a framework-neutral shared simulation
runtime. A plugin describes one simulation; it does not own mutable learner or UI state. Small typed
protocols provide behavior so existing functions and dataclasses can be enrolled without class
hierarchies or physics rewrites.

The target flow is:

```text
Streamlit adapter now / web adapter later
  -> LearningRuntime
       -> Curriculum and learner-progress services
       -> SimulationRuntime
            -> SimulationPlugin
                 -> pure Python model runner
                 -> renderer-neutral result and render specification
       -> Notebook and achievement services
  -> persistence port (local profile store initially)
```

Neither Streamlit nor JavaScript may call a physics model through a second scientific
implementation. Python models remain authoritative.

### SimulationPlugin

`SimulationPlugin[P, R]` is a frozen descriptor assembled in the owning simulation slice. It has
the following required parts:

| Part | Contract and ownership |
| --- | --- |
| Identity | Stable simulation ID, title, subject, concepts, model version, central question, assumptions, limitations, and discovery metadata. Existing IDs remain unchanged. |
| Parameter schema | A renderer-neutral ordered schema of typed fields, units, ranges, choices, defaults, help, grouping, and commit policy. It validates input and converts validated values to `P`; it contains no Streamlit widgets. |
| Model runner | A callable `run(P, seed) -> R` around the existing pure Python entrypoint. Identical committed input, seed, and model version must be deterministic. |
| Result contract | A typed immutable result exposing parameters, metrics, events, plots or sampled tracks, warnings, assumptions, outcome description, seed, and model version. Existing `ContractResult` remains the common envelope while specialized result types remain allowed. |
| Renderer | A renderer-neutral `RenderSpec` builder from `R`, mode, and accessibility preferences. Streamlit embeds the current player/chart documents; a web client can consume the same serialized spec. Renderers never alter scientific results. |
| Mode capabilities | Declared capabilities for Explore, Compare, Analyze, and Model, including prediction, controlled comparison, analytical representations, equations, assumptions, and limitations. A mode may supply simulation-specific content without owning navigation. |
| Notebook codec | Converts a committed run to a versioned `TrialRecord` payload and restores supported parameters. It owns simulation-specific serialization, not notebook storage or widgets. |
| Lesson/activity integration | Stable activity actions: apply a setup, request a mode, run, compare, inspect evidence, and reflect. Lessons refer to plugin and action IDs, never page functions. |
| Assessment hooks | Pure evidence extractors from parameters, result, events, and notebook observations. They return typed evidence; assessment policy decides correctness and attempts. Hooks do not mutate progress or award badges. |
| Accessibility description | A nonvisual system description, coordinate convention, parameter summary, outcome description, and renderer-specific alternative representation. Keyboard and motion behavior remain adapter responsibilities. |
| Model-version migration | An ordered set of pure migrations for persisted parameter/result references. A plugin must either migrate an older version or return an explicit unsupported-version result; silent reinterpretation is forbidden. |

The descriptor may compose existing dataclasses and callables. It must not grow methods for
navigation, persistence, authentication, analytics, or Streamlit rendering.

### Shared simulation runtime

`SimulationRuntime` is an application service with explicit input and output values. Its state is
keyed by simulation ID and contains:

- `editing_parameters`: valid or partially valid UI input;
- `committed_parameters`: the last validated setup used for execution;
- seed and model version;
- the latest result or structured execution error;
- optional comparison baseline;
- active learning mode and prediction state.

Editing a control does not imply a run. The parameter schema declares whether a field uses an
explicit commit or continuous commit; the runtime uses the same transition for both. This
preserves continuous-feedback simulations without making every Streamlit rerun scientific state.

The execution sequence is fixed:

1. collect and parse editing values through the parameter schema;
2. validate and commit a complete setup;
3. compute a cache key from plugin ID, model version, canonical parameters, and seed;
4. execute the pure runner through the existing bounded cache policy;
5. translate expected validation, numerical, and resource failures into typed user-facing errors;
6. expose result metrics and renderer specifications;
7. optionally record exactly one notebook trial for an explicit record action;
8. evaluate mission and assessment evidence without side effects;
9. publish typed notebook, achievement, activity, assessment, and progress events.

Unexpected programming errors remain visible to diagnostics and tests; they are not converted to
successful empty results. Runtime events are synchronous values handled by the application
boundary. This is not a message bus.

Mode navigation is shared and capability-driven. Plugins provide mode content and evidence, while
the runtime owns selection, committed state, and transitions. Metrics are typed values with units;
presentation adapters choose cards, tables, static charts, or interactive charts.

### Educational domains

The domains remain separate but use stable identifiers and typed events:

- **Curriculum:** subjects, ordered units, lessons, objectives, prerequisites, concepts, and
  course navigation. It references simulations and assessments by ID.
- **Lessons:** authored explanations, derivations, examples, misconceptions, limiting cases, and
  ordered activity references. Content remains immutable and outside model code.
- **Activities:** learner actions and required evidence. An activity may invoke plugin actions but
  cannot reach Streamlit session state.
- **Assessments:** question or performance definitions, answer/evidence evaluators, attempts, and
  feedback. Assessment definitions are content; pure evaluation is domain logic. Scores do not
  belong in simulation results.
- **Learner progress:** completion of lessons, activities, objectives, and assessments. Progress is
  derived from typed events and persisted independently of rendering.
- **Notebook:** versioned trials, comparisons, predictions, observations, and reflections. It owns
  records, not course completion rules.
- **Achievements:** optional recognition derived from mission or progress evidence. Existing
  mission and badge IDs remain compatible; achievements never gate course access.

`LearningRuntime` coordinates these services for a lesson session. It may call
`SimulationRuntime`, assessment evaluation, notebook operations, and progress reduction, but it
does not contain physics or authored lesson text.

## Dependency and ownership rules

Dependencies point inward:

```text
Streamlit pages / future web API / browser renderers
  -> application runtimes and ports
       -> education, notebook, achievement, and simulation contracts
            -> pure slice physics and shared numerical utilities
```

1. Slice `physics.py` modules depend only on standard scientific/domain utilities; they never
   import Streamlit, education, persistence, presentation, canvas, or frontend code.
2. Plugin descriptors and codecs live in their simulation slice and may import that slice's
   physics, metadata, missions, and renderer-spec builders. Physics never imports the plugin.
3. Education content may reference plugin, activity, assessment, objective, and concept IDs but
   never imports pages, renderers, or persistence adapters.
4. Domain services do not read `st.session_state`. A Streamlit adapter maps widget state to runtime
   commands and renders returned view data.
5. Persistence is behind small repositories for profiles, progress, and notebooks. The initial
   implementation may adapt the existing local SQLite/JSON store; no remote repository is required.
6. Browser code consumes versioned JSON render specifications and returns interaction intent only.
   It does not integrate motion, grade answers, or mutate authoritative progress.
7. Central catalogs discover and validate slice-owned descriptors. They do not duplicate
   simulation metadata or contain simulation-specific branches.

## Existing abstraction disposition

### Remain

- Pure slice `physics.py` models, validation, units, integrators, and simulation IDs.
- `ContractResult` and its metric, event, plot, animation, assumption, and mission values.
- Typed education models and validation, `PathwayProgress`, `ExperimentNotebook`, `TrialRecord`,
  mission definitions/evaluators, application events, accessibility preferences, state-key
  namespacing, and the shared player/frontend source tree.
- Local `ProfileStore` as the temporary persistence adapter.

### Consolidate

- `SimulationDefinition`, `ExpansionDefinition`, model metadata, page/canvas entrypoints, and
  capability declarations become one discovered plugin descriptor. Existing records may back the
  compatibility adapter during migration.
- The two repeated page-controller families move into `SimulationRuntime` plus one Streamlit
  simulation host. Slice pages reduce to plugin-specific parameter, content, and render adapters.
- Notebook setup handoff and page-specific restoration become the plugin notebook codec and a
  shared apply-setup command.
- Mission evidence and future assessment evidence share a side-effect-free evidence shape while
  retaining distinct mission and assessment policies.
- Lesson progress callbacks, notebook callbacks, and badge callbacks use one typed application
  event union and existing synchronous publisher.

### Deprecate

- Direct page entrypoint loading as the normal runtime path.
- Raw page-owned `learning_mode`, committed-run, comparison, and notebook-restoration state.
- String import paths in expansion manifests once a plugin descriptor is discoverable.
- Page functions that both execute physics and render Streamlit output.
- Persisted aliases for legacy session keys after their documented release window.

### Delete after migration

- `ExpansionDefinition`, its duplicate catalog, and validation rules that are fully represented by
  plugin validation.
- Page-controller boilerplate and simulation-specific setup-handoff parsing.
- Compatibility imports or adapters with no remaining registered plugin or persisted-state reader.
- Duplicate metadata records after registry, home, missions, and curriculum all consume plugins.

Deletion occurs only after repository-wide import searches, migration tests, and persisted-record
fixtures prove that the compatibility path has no supported consumer.

## Rejected alternatives

### Rewrite all 22 simulations before course work

Rejected because it delays the Mechanics course, creates a high-risk flag day, and provides no
incremental learner value. Old and new page paths must coexist behind one registry during migration.

### Move physics into TypeScript

Rejected because the tested Python models are scientific authority. A web frontend should call a
Python boundary or consume versioned precomputed results/render specifications.

### Keep adding helpers inside each Streamlit page

Rejected because the measured duplication is orchestration, not merely formatting. More page
helpers would preserve page-owned state and make a web migration harder.

### One base class for every simulation, lesson, and renderer

Rejected because inheritance would couple unrelated variation and force existing functions into a
large lifecycle. Frozen descriptors plus small protocols allow gradual adoption.

### Event bus, workflow engine, service mesh, or generalized plugin marketplace

Rejected as speculative. One in-process runtime, typed synchronous events, and local adapters meet
the current product need.

### Replace Streamlit immediately

Rejected because the course and shared runtime must establish the product behavior first. The
framework-neutral contracts create the migration seam without financing two incomplete products.

## Migration stages

Each stage ends with a runnable application and the complete quality gates. Physics outputs,
simulation IDs, notebook restoration, missions, accessibility, and all four modes are parity gates.

1. **Contracts and adapter:** introduce plugin, parameter-schema, runtime-command/result,
   render-spec, evidence, and migration contracts. Build a read-only adapter that constructs
   plugins from current registry/manifests without changing page routing.
2. **Runtime pilot on Cannonball:** host Cannonball through `SimulationRuntime` and the shared
   Streamlit host. Preserve its lesson, forms/fragments, interactive charts, notebook records,
   missions, query links, and old session-state reads.
3. **Mechanics course foundation:** define the Mechanics subject/unit sequence, reusable activity
   and assessment contracts, progress reduction, and lesson host. Author course lessons against
   plugin actions rather than page functions; do not require other subjects to migrate.
4. **Mechanics enrollment:** migrate Mechanics simulations one at a time, prioritizing course use.
   Each plugin replaces only its own page orchestration after model, notebook, mission, mode,
   accessibility, AppTest, and browser parity passes.
5. **Remaining simulation enrollment:** adapt the other 13 simulations opportunistically. The
   registry can route migrated IDs to the shared host and unmigrated IDs to existing pages.
6. **Web boundary:** expose the same catalog, parameter schema, runtime commands/results,
   render specifications, curriculum, notebook, assessment, and progress contracts through a
   versioned Python API. Build a web client only after the Mechanics course proves the contracts.
7. **Compatibility removal:** remove duplicate manifests, old controllers, state aliases, and
   direct page routing only when the conditions below are satisfied.

## Transitional compatibility removal conditions

- **Legacy page route:** remove per simulation after that plugin passes numerical/result parity,
  four-mode AppTest coverage, notebook restore/record fixtures, mission parity, and representative
  accessibility/render tests; remove the global fallback only when all 22 IDs use the shared host.
- **Expansion manifest adapter:** remove when all 22 plugins declare equivalent entrypoints,
  assumptions, limitations, capabilities, missions, accessibility requirements, and validation
  evidence, and no production or test import remains.
- **Session-state aliases:** remove only after the documented compatibility window and a fixture
  proves current profiles/notebooks restore without them. Absence of repository imports alone is
  insufficient because browser sessions may persist.
- **Setup handoff compatibility:** remove when every supported notebook trial is restored through a
  plugin codec and no page parses a raw setup dictionary.
- **Old result/model versions:** remove a migration only when the support policy no longer promises
  that version and representative exported profile/notebook fixtures have a newer canonical form.
- **Direct Streamlit page functions:** remove after registry, home, lesson links, query routing, and
  tests resolve the corresponding plugin host instead.

## Explicit non-goals

- Adding simulations or changing physics equations.
- Accounts, organizations, classrooms, teacher dashboards, LMS integration, real-time
  collaboration, cloud synchronization, or multi-tenant authorization.
- A generic plugin marketplace, dynamic third-party code loading, or stable external plugin SDK.
- Microservices, queues, event sourcing, CQRS, or distributed caches.
- Adaptive tutoring, automated curriculum generation, high-stakes grading, or psychometric learner
  models.
- Replacing every Matplotlib chart without a named interactive learning task.
- Selecting a web framework before the versioned runtime and course contracts are proven.
- Maintaining two independent physics engines in Python and JavaScript.

This ADR accepts an incremental application architecture, not a new platform program: build the
Mechanics course, extract repeated orchestration as it is exercised, preserve all 22 simulations,
and make every transitional layer earn a concrete removal condition.
