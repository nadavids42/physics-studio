# Mechanics milestone release-readiness report

Audit date: 2026-07-18. Verdict: **ready for a limited local milestone release**, not ready to be
described as a complete Mechanics course, undergraduate textbook, hosted classroom platform, or
WCAG-conformant product.

## Verified capabilities

- The two accepted ADRs match the implementation boundary: Python remains authoritative for
  physics; Streamlit is the compatibility host; Gas Laws and Cannonball use the typed plugin and
  shared runtime; the linked projectile experience uses the versioned frontend protocol. Semantic
  architecture and import-cycle tests pass.
- All 22 simulations remain independently discoverable and runnable. Stable IDs and slice-owned
  model versions feed registry metadata, plugins, notebook trials, cache keys, and replay.
- The active Mechanics curriculum contains five connected lessons from scientific models and
  measurement through projectile motion. Its prerequisite graph, lesson references, objective
  coverage, assessment definitions, units, tolerances, and private answer keys validate.
- Lesson completion requires activity/checkpoint evidence rather than visitation. Attempts and
  objective evidence are distinct from progress. Lessons resume at the last incomplete section,
  and learner answers survive unrelated reruns.
- SQLite is authoritative for local learners. Schema 1–3 profiles migrate to normalized schema 4;
  progress, attempts, trials, notebook entries, evidence, achievements, and preferences survive
  reload. Writes are transactional, malformed child records are quarantined, and export/import
  round trips are tested.
- Notebook trials record simulation ID, canonical parameters, seed where applicable, and model
  version. Setup handoff and Cannonball replay preserve deterministic targets and committed state.
- Automated Chromium checks pass for keyboard behavior, reduced motion, high contrast/forced
  colors, linked readouts, narrow viewports, lifecycle cleanup, and visual baselines. The 320 px
  linked experience has no horizontal overflow. Deterministic bundle, payload, sample, cache, and
  mount budgets pass.
- A clean Python 3.11 virtual environment installed `.[dev]`, imported the package, and discovered
  22 simulations. A clean `npm ci` succeeded with no reported vulnerabilities. Isolated sdist and
  wheel builds succeeded.

## Test evidence

| Gate | Result |
| --- | --- |
| Architecture/course/persistence/runtime release subset | 138 passed |
| Full Python suite | 555 passed, 3 skipped |
| Ruff format and lint | passed |
| Configured strict MyPy ratchet | passed, 18 source files |
| Frontend Prettier, ESLint, Vitest, deterministic build | passed; 21 Vitest tests |
| Chromium accessibility, linked-runtime, and visual checks | 7 passed |
| Performance budgets | passed |
| Clean Python contributor install | passed on Python 3.11 |
| Clean frontend install | passed on Node 22 |
| Isolated package build | sdist and wheel passed |

The three default-suite skips are browser-conditional tests; they passed when rerun with the
available Chromium executable. Python 3.12 and 3.13 remain CI-matrix responsibilities and were not
locally re-created in this audit.

## Explicit limitations and unsupported classroom features

- Only the first five connected Mechanics lessons are authored. The 24-lesson, eight-unit roadmap
  is a validated specification, not learner-visible course coverage. Forces, energy, momentum,
  rotation, gravitation, and cumulative Mechanics review are not yet implemented as lessons.
- There is no authentication, hosted synchronization, multi-device conflict resolution, roster,
  enrollment, assignment workflow, teacher dashboard, grading book, standards report, classroom
  analytics, accommodation workflow, or institution administration.
- Constructed responses are stored for learner self-review; the system does not claim to grade
  open reasoning. There is no adaptive sequencing or automated diagnosis beyond declared
  misconception tags and remediation references.
- Local SQLite is appropriate for development and single-user use, not simultaneous classroom
  deployment. Streamlit session state remains an active UI cache.
- Offline installation is not guaranteed because initial Python and npm dependency installation
  requires available packages. The built runtime itself does not require Node.
- Automated accessibility checks do not establish WCAG conformance. Real keyboard, screen-reader,
  200%/400% zoom, native forced-colors, mobile-device, and learner usability sessions remain
  required before broader deployment.

## Known technical debt

- The import/distribution name remains `physics_playground`; changing it requires a versioned
  compatibility plan.
- `InteractiveMode`/`SimulationMode` and Kid/Expert import shims, legacy session-key migration,
  setup-handoff compatibility, `LocalProfile`/`ProfileStore`, legacy profile tables/imports, and
  frontend protocol v1 remain supported compatibility code with removal conditions documented in
  ADR-002, architecture, and persistence documentation.
- MyPy is a strict 18-module ratchet, not repository-wide type coverage. Browser delivery still
  uses Streamlit component documents while the dedicated frontend protocol is introduced one
  simulation at a time.

## Known educational gaps

- The active sequence compresses roadmap topics and uses stable implementation IDs that do not
  map one-to-one to every roadmap lesson. The roadmap must not be presented as completed content.
- Vector fundamentals and right-triangle trigonometry are prerequisite-sensitive around projectile
  motion. Learner testing is needed to determine whether the current in-lesson component support is
  sufficient.
- Assessment evidence is credible for the implemented objectives but narrow; transfer validity,
  reading load, hint effectiveness, and spoken-equation accessibility require observation with
  target learners.
- No cumulative assessment yet demonstrates durable transfer across even the five implemented
  lessons. The current final projectile lesson integrates representations but is not a course-wide
  Mechanics review.

## Recommended next course-development step

Do not expand to another subject. First reconcile the active lesson IDs and scope with the roadmap,
then author the next coherent Mechanics bridge: vector foundations and one-dimensional/free-fall
synthesis leading into forces and free-body diagrams. Include a cumulative assessment over the
existing five lessons and conduct learner/assistive-technology usability sessions before calling
the milestone a complete introductory Mechanics unit.
