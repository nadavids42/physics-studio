# Changelog

Notable project changes are recorded here. This project follows the structure of
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), although historical development was
not consistently tagged as releases.

## Unreleased

### Added

- Contributor-facing packaging, Ruff, MyPy, pytest, pre-commit, and GitHub Actions configuration.
- Architecture, expansion, development, contribution, and migration documentation.
- Apache-2.0 licensing.
- A framework-free ES-module frontend workspace with Prettier, ESLint, Vitest, esbuild, packaged
  static assets, and behavioral scene/player/chart tests.
- Typed curriculum, lesson, activity, worked-example, guided-derivation, misconception,
  checkpoint, audience, and progress models.
- The first complete persisted learning pathway: projectile motion from components.
- Subject/unit/concept navigation with stable query identifiers, search, and optional next-lesson
  recommendations.
- A typed interactive chart contract with hover, zoom, linked highlighting, and accessible tables.
- Chromium perceptual visual regression and real-browser accessibility verification.
- A final Principal Architect audit with issue dispositions, revised grades, and readiness verdicts.

### Changed

- Reformatted Python source and established lint and type-checking ratchets without changing
  simulation behavior.
- Replaced the historical implementation log in the README with a concise project overview.
- Migrated all 22 simulations to subject-based vertical slices with slice-owned registry and
  mission metadata discovered by central validated catalogs.
- Replaced ambiguous shared-module names and removed compatibility shims after repository-wide
  consumer checks.
- Standardized physical constants and namespaced simulation/application state keys.
- Replaced hidden mission/profile/accessibility dependency cycles with a typed callback seam.
- Adopted shared RK4 and velocity-Verlet helpers in real simulations and removed speculative
  one-consumer binding, preset, example, and duplicate generic model frameworks.
- Added audience-neutral shared copy with persisted Explorer, Core, and Advanced presentation
  dimensions.
- Added linear force-vector scaling and legends for inclined-plane diagrams plus explicit
  physical, normalized, and schematic vector semantics.
- Added measured Cannonball forms, fragments, scan/document caches, and player-state preservation
  as the repository performance reference pattern.
- Improved player keyboard behavior, scrubber announcements, semantic grouping, iframe focus, and
  reduced reliance on `!important` CSS.

## 1.0.0 - 2026-07-18

This entry summarizes the current baseline. Earlier work landed incrementally and was not
maintained as a versioned changelog.

### Added

- A 22-simulation registry spanning mechanics, oscillations, gravity, waves, optics,
  electromagnetism, fluids, gases, and diffusion.
- Explore, Compare, Analyze, and Model modes across registered simulations.
- Typed parameter/result models, numerical validation, computation budgets, deterministic seeds,
  and model-focused tests.
- Shared requestAnimationFrame browser player with responsive high-DPI canvas rendering, playback
  controls, stepping, scrubbing, reduced-motion handling, and teardown.
- Shared scientific design tokens, semantic vectors, reusable assets, three presentation levels,
  chart styling, and structural visual regression coverage.
- Structured missions and badges, experiment notebook capture and reuse, local SQLite profiles,
  profile import/export, and HTML/Markdown/CSV/JSON lab reports.
- Accessibility preferences for reduced motion, high contrast, and larger text, plus keyboard and
  nonvisual chart/result support.
- Subject-oriented vertical slices and validated expansion manifests for 22 simulations.

### Architecture notes

- Streamlit remains the current delivery platform. Physics models and educational content are
  deliberately independent of it so presentation can evolve separately.
