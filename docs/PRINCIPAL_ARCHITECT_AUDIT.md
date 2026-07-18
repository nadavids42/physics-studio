# Final principal-architect audit

Audit date: 2026-07-18

This audit rechecks the repository against the original Principal Architect Review and the product
ambition: an accessible, visually polished interactive physics textbook for high-school through
introductory undergraduate learners that can grow beyond a simulation gallery. The code, tests,
packaging, built frontend assets, running Streamlit application, and current documentation are the
authority; earlier migration reports are historical evidence only.

## Executive verdict

Physics Studio is now a coherent beta-quality open-source educational platform foundation rather
than the split personal-project architecture described by the original review. Its strongest
assets remain trustworthy pure physics, unusually deliberate accessibility, and the
Predict–Explore–Compare–Analyze–Model learning loop. The repository now adds consistent vertical
slices, discoverable metadata, a real JavaScript toolchain, behavioral and browser tests, scalable
navigation, typed lesson models, one complete learning pathway, and normal contributor tooling.

The ambition is not fully realized. Twenty-one simulations still lack authored lesson pathways;
most performance work is proven on Cannonball rather than applied uniformly; type checking covers
a ratchet rather than the full package; contextual art and a distinctive visual identity remain
uneven; and Streamlit/local SQLite are not a classroom-scale multi-user delivery stack. Those are
bounded product and delivery debts, not evidence that the physics or presentation architecture
needs another rewrite.

## Original ranked issues

| # | Original issue | Status | Current evidence and rationale |
|---:|---|---|---|
| 1 | Dual horizontal/vertical architecture and missing plan | **Resolved** | All 22 simulations are subject-based vertical slices. Registry and mission metadata are slice-owned and discovered centrally. Architecture and migration documents exist. |
| 2 | Rendering logic trapped in Python JavaScript strings | **Resolved** | Editable runtime, assets, vectors, interactions, charts, and scenes are ES modules under `frontend/src`; esbuild produces packaged static assets. Python validates and serializes payloads. |
| 3 | Compressed, unreviewable Python style | **Resolved** | Ruff formatting covers the tree and CI/pre-commit enforce it. Remaining long lines are formatted data or generated assets rather than a second coding style. |
| 4 | No packaging, CI, license, lint, type, or contributor setup | **Resolved** | Installable `pyproject.toml`, Apache-2.0, Ruff, MyPy ratchet, pytest, pre-commit, GitHub Actions, Python-version policy, and contributor docs are present. |
| 5 | String/hash presentation tests; no JS or AppTest coverage | **Resolved** | Vitest executes player, chart, visual, and scene behavior. AppTest covers shell/navigation and representative pages. Contract, perceptual, and real-browser accessibility tests replace source-token checks. |
| 6 | Child-oriented voice conflicts with HS/undergraduate audience | **Substantially improved** | Explorer/Core/Advanced dimensions separate voice, mathematical depth, and visual density; Core is neutral default. Shared shell and first pathway are migrated. Some simulation names, emoji, and legacy page copy remain playful. |
| 7 | Player state dies on every Streamlit rerun | **Partially improved** | Stable keys, forms, fragments, payload caching, and player-signature tests preserve state across unrelated Cannonball changes. A changed physical run intentionally remounts. The pattern is not yet applied uniformly and iframe-local state cannot survive every Streamlit remount. |
| 8 | Mission/profile/accessibility/player cycles hidden by lazy imports | **Resolved** | A small typed synchronous callback seam connects domain events to persistence at the application boundary. Domain services do not import Streamlit UI and failures propagate. |
| 9 | No lesson, curriculum, or progression model | **Substantially improved** | Typed subjects, units, lessons, sections, objectives, prerequisites, derivations, examples, misconceptions, checkpoints, activities, and progress events exist with validation. One complete persisted projectile pathway proves the model; catalog breadth is still one lesson. |
| 10 | No rendered visual verification | **Resolved** | A small Chromium/Pillow perceptual suite covers mechanics, oscillation, optics, light/dark, high contrast, reduced motion, and mobile layouts without hundreds of brittle goldens. |
| 11 | Speculative bindings/presets/integrators/examples | **Resolved** | One-consumer binding and example frameworks were deleted; setup handoff was retained; shared RK4 and Verlet integrators have multiple live model consumers; YAGNI decisions are documented. |
| 12 | Duplicated physical constants | **Resolved** | Shared SI constants are actively used across models. Remaining `9.81` occurrences are the canonical declaration and an explicit worked-example substitution, not competing defaults. |
| 13 | Misleading nonlinear force-vector lengths | **Resolved** | Inclined-plane forces use a documented linear pixels-per-newton scale and canvas legend. Shared vectors declare physical, normalized, or schematic semantics and require disclosure when not scaled. |
| 14 | Flat sidebar cannot scale | **Resolved** | Home is the discovery surface; sidebar navigation is bounded by subject, unit/collection, and concept. Registry and curriculum metadata drive it, with stable query IDs and optional recommendations. |
| 15 | README drift and phantom paths | **Resolved** | Project-facing paths and commands are verified and documentation is split by purpose. This audit corrected newly accumulated frontend and migration-status drift. |
| 16 | Fragile `!important` high-contrast CSS without browser checks | **Substantially improved** | Real Chromium coverage verifies focus, high contrast, large text, reduced motion, narrow layout, and controls. Unnecessary overrides were removed; nine remain where user preferences must override Streamlit or authored animation. Outer Streamlit DOM remains a framework boundary. |
| 17 | Untyped public helpers | **Partially improved** | Ruff and an intentionally strict MyPy ratchet pass on 15 foundation source targets. Typed domain/content/event/chart models are strong, but repository-wide strict typing is not yet achieved. |
| 18 | Uncached scans and rerun-heavy Matplotlib | **Partially improved** | Bounded data/document caches, timing instrumentation, Cannonball forms/fragments, cached scans, and a browser-native chart proof are measured. Most slices still use static Matplotlib and have not adopted the reference interaction pattern. |
| 19 | Emoji density and anonymous visual identity | **Partially improved** | Semantic tokens, scientific assets, three experience levels, consistent illustrations, and restrained new shell copy create a coherent vocabulary. Several page headers/buttons and metadata icons still lean on emoji, and contextual scenes remain sparse. |
| 20 | Static-only charts | **Substantially improved** | A typed interactive chart contract supports hover, linked highlighting, zoom, line/marker encodings, descriptions, and tables. It is deliberately proven on representative Cannonball views rather than mechanically replacing useful static plots. |
| 21 | Missing misconception/model-limit bridges | **Partially improved** | The lesson model supports misconception callouts, progressive derivations, worked examples, assumptions, units, validation, and limiting cases; projectile and inclined-plane accuracy work prove the pattern. Coverage is not yet curriculum-wide. |
| 22 | Audience not first-class | **Resolved** | Audience, voice, mathematical depth, and visual density are independent persisted dimensions; physics inputs/results are invariant across them. Content blocks can select depth without triplication. |

### Original quick wins

Formatting/CI, packaging/license, documentation repair, shadowed imports, scalable navigation,
Cannonball forms/caching, and force scale legends are complete. The recommendation to wrap every
Explore control in a form was **rejected as a blanket rule**: continuous feedback remains
appropriate where it is itself the learning activity. The repository documents a case-by-case
performance rule instead.

## Current architecture and scalability

The runtime is a registry-driven Streamlit application over 22 validated vertical slices. Each
slice owns physics, page composition, mission evaluation, and registry/mission metadata. Subject
manifests add implementation and accessibility contracts. Central catalogs discover and validate;
they do not accumulate simulation definitions. Physics modules have no Streamlit, Matplotlib,
canvas, profile, or lesson-renderer dependencies.

The browser boundary is explicit: Python constructs validated, deterministic payloads; JavaScript
renders and interacts. This makes a future non-Streamlit frontend plausible without moving physics
into the browser. Remaining portability work is chiefly a versioned external component/API,
externalized persistence, removal of transitional browser globals, and a stable transport for
payloads—not a rewrite of simulation models.

Scalability to hundreds of catalog entries is credible at the metadata/navigation level. It is not
yet credible for hosted classrooms: profiles are local SQLite/JSON, there is no authentication or
multi-tenant service, and Streamlit retains one WebSocket-driven session per learner.

## Educational and product readiness

The educational domain can represent serious textbook content: objectives, prerequisites,
concepts, progressive derivations, worked examples with substitutions and unit checks,
misconceptions, checkpoints, simulation phases, reflection, completion, audience depth, and next
lessons. Progress persists through the existing profile callback seam and direct access to all four
modes remains available.

The bottleneck is now authorship and editorial governance. Only projectile motion has a complete
pathway. Adding curriculum at scale should proceed with subject/unit sequencing, content review,
formula and unit tests, and reusable authoring examples rather than inventing more content models.

## Verified test and quality metrics

| Gate | Result |
|---|---|
| Ruff format | 286 files checked; pass in 0.01 s |
| Ruff lint | Pass in 0.01 s |
| MyPy ratchet | 15 source targets; no issues in 0.19 s |
| Complete Python suite | 459 passed, 2 browser-dependent skips; 11.29 s pytest time, 11.96 s wall time |
| Streamlit AppTest suite | 12 passed in 6.69 s, covering home, navigation, lesson routing, Cannonball interaction, preferences/errors, and one page per subject |
| Frontend | Prettier pass; ESLint pass; 15 Vitest tests pass; deterministic build check pass in 6.69 s total |
| Real-browser checks | Chromium accessibility and perceptual suites: 2 passed in 7.93 s |
| Package | Source distribution and wheel build successfully with installed build requirements in 1.88 s |
| Application smoke | Streamlit server started, health endpoint returned `ok`, root shell responded, and representative pages passed AppTest |

Coverage.py is not configured, so no percentage is claimed. The first isolated package-build
attempt could not download build requirements because the audit sandbox has no network access;
the same build completed with `--no-isolation` using the already installed declared requirements.

## Remaining technical debt, ranked

### High

1. **Curriculum breadth and editorial QA:** one complete lesson cannot yet support a course or prove
   cross-unit progression.
2. **Hosted identity and persistence:** local profiles are appropriate for the current beta but not
   classrooms, shared devices, or multi-user deployment.
3. **Type coverage:** the strict ratchet covers foundation modules, not all 216 Python modules or
   Streamlit page adapters.

### Medium

4. **Performance adoption:** forms/fragments/interactive charts are proven chiefly on Cannonball;
   representative profiling should drive migration of the slowest remaining pages.
5. **Streamlit iframe boundary:** outer iframe naming is limited by the public API, each iframe
   retains its own bundle/runtime, and playback state cannot survive every remount.
6. **Visual identity/contextual breadth:** shared assets are consistent, but contextual scenes and
   original illustration direction are not equally mature across all subjects.
7. **Shared notebook/report widget keys:** simulation keys are namespaced, while a small set of
   shared Streamlit widget keys remain feature-prefixed strings rather than `feature_key()` values.

### Low

8. **Manual accessibility matrix:** automated semantics are strong, but NVDA, VoiceOver, browser
   zoom, and forced-colors checks remain a manual release checklist.
9. **Transitional frontend globals:** scene registration still exposes compatibility globals inside
   isolated player documents.
10. **Historical migration document:** useful as provenance, but necessarily verbose and stale in
    its original baseline sections; current docs explicitly label it historical.

## Next three product investments

1. **Author a coherent mechanics unit of 5–8 lessons** using the existing pathway model, with
   editorial/scientific review and meaningful prerequisite/next-lesson sequencing.
2. **Establish hosted learner identity and persistence boundaries** behind the existing event and
   profile interfaces before attempting teacher dashboards or classroom analytics.
3. **Run a measured interaction-and-visual polish wave** on the highest-use simulations: apply the
   proven performance pattern where profiling warrants it, expand contextual illustration, and
   migrate only charts with a named interactive learning task.

## Readiness verdicts

- **Outside contributors:** **Yes, with normal maintainer review.** Setup, license, CI, formatting,
  tests, architecture guides, vertical-slice ownership, and contribution rules are suitable for
  external pull requests. Contributors should be told that MyPy is a ratchet and browser goldens
  require intentional inspection.
- **Curriculum content at scale:** **Architecturally yes; operationally not yet.** The content model
  and validation are ready. The project still needs a subject-level editorial plan, more examples,
  and reviewer ownership before accepting large volumes of lessons.

## Revised grade

| Category | Original | Current | Assessment |
|---|---:|---:|---|
| Architecture | C+ | **A−** | One vertical architecture, explicit boundaries, slice discovery, and no hidden dependency cycle. |
| Maintainability | C− | **B+** | Normal tooling and readable code; incomplete type coverage and some Streamlit-specific repetition remain. |
| Educational quality | B− | **B** | Strong learning model and one excellent pathway, but insufficient curriculum breadth. |
| Visual design | B− | **B+** | Verified shared identity and accurate vectors; contextual breadth and distinctiveness remain uneven. |
| Performance | C+ | **B+** | Instrumented, bounded, and proven reference optimizations; Streamlit and incomplete adoption set the ceiling. |
| Scalability | C | **B+** | Catalog/content architecture scales; hosted multi-user delivery does not yet. |
| Accessibility | B+ | **A−** | Real browser behavior, strong preferences and alternatives; manual AT checks and iframe limits remain. |
| Code quality | C | **B+** | Consistent formatting, validation, typed domains, and CI; strict typing is not repository-wide. |
| Testing | B− | **A−** | Fast physics tests plus JS, AppTest, behavioral browser, accessibility, and perceptual coverage. |
| Overall polish | C+ | **B+** | Credible public beta foundation, not yet a complete interactive textbook or classroom platform. |

The candid conclusion is that Physics Studio is now worthy of its physics core and ready to grow
through content and focused product work. It should resist another architecture program until real
contributors, learners, profiling, or classroom requirements expose a concrete limitation.
