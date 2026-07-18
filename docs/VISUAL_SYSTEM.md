# Physics Studio visual system

Physics Studio aims to be an interactive physics textbook where every figure is alive. The visual system makes figures polished and approachable without allowing presentation to change, obscure, or exaggerate the physics.

## Architecture

The rendering pipeline deliberately keeps calculation separate from presentation:

```text
typed parameters → pure physics model → typed result / immutable tracks
                                      → shared browser player
                                      → shared assets and annotations
                                      → simulation scene composition
```

The important folders are:

```text
physics_playground/
├── models/                 # Numerical and analytical physics; renderer-neutral
├── visual/
│   ├── tokens.py           # Colors, type, spacing, strokes, motion, breakpoints
│   ├── css.py              # Generated application and iframe CSS
│   ├── primitives.py       # Low-level themed Canvas helpers
│   ├── assets.py           # Typed AssetSpec and PhysicsAssets library
│   ├── vectors.py          # Vector semantics and PhysicsAnnotations
│   ├── animation.py        # Presentation-only camera and effect helpers
│   ├── experience.py       # Diagram, Illustrated, and Contextual levels
│   └── contrast.py         # WCAG contrast validation
├── canvas/
│   ├── player.py           # Playback, controls, scaling, lifecycle, accessibility
│   └── *.py                # Small scene adapters for simulation families
└── presentation/
    ├── chart_system.py     # Shared Matplotlib styling
    └── accessibility_ui.py # Display preferences and chart descriptions
```

Do not put physics integration, unit conversion, mission evaluation, or notebook mutation in a scene adapter. Scene code consumes recorded results; it does not revise them.

The canonical entrypoints are `visual/tokens.py`, `visual/assets.py`, `visual/vectors.py`, `canvas/player.py`, and `presentation/chart_system.py`. Extend those shared modules before creating a parallel simulation-specific mechanism.

## Design principles

1. **Meaning before decoration.** Geometry, relative position, vector direction, labels, units, and scale disclosures have priority over atmosphere.
2. **Semantic consistency.** The same physical quantity uses the same token across simulations. Do not choose colors by local taste.
3. **Progressive enhancement.** A Diagram view remains understandable without gradients, shadows, particles, camera motion, or contextual scenery.
4. **Model authority.** Physical motion comes from model samples. Interpolation and visual effects are presentation only.
5. **Restrained depth.** Illustrated objects may use a soft highlight, outline, and shadow. Avoid glossy, cartoonish, or game-like treatment.
6. **Textbook clarity.** Labels, equations, axes, units, and annotations must remain readable at narrow widths.
7. **Shared solutions.** Add a token, asset, annotation, or chart helper when a need applies to more than one simulation. Avoid simulation-specific CSS.

## Semantic color usage

Use `LIGHT_THEME`, `DARK_THEME`, or the renderer's `PhysicsVisuals.token()` helper. Never copy a hex value from another scene.

| Meaning | Token |
|---|---|
| Velocity | `velocity` |
| Acceleration | `acceleration` |
| Net force | `net_force` |
| Gravity | `gravity` |
| Normal force | `normal_force` |
| Friction | `friction` |
| Tension | `tension` |
| Electric field | `electric_field` |
| Magnetic field | `magnetic_field` |
| Displacement | `displacement` |
| Energy | `energy` |
| Trajectory | `trajectory` |
| Uncertainty/reference data | `uncertainty` |
| Selected object | `selected` |

Graph series use `graph_1` through `graph_7`. Series must also differ by line style and marker where multiple datasets are compared. Color must never be the only carrier of meaning.

Canvas example:

```javascript
const color = PhysicsVisuals.token(frame, 'colors', 'velocity', '#087EA4');
```

The final argument is a defensive fallback for progressive enhancement, not a new local palette.

## Adding a new asset

1. Add a stable value to `AssetKind` in `visual/assets.py`.
2. Implement a function inside `PhysicsAssets` using `setup()`, `colors()`, shared tokens, and `finish()`.
3. Add the function to the library map so `PhysicsAssets.draw()` can resolve it.
4. Support the common configuration where it is meaningful:
   - `x`, `y`, `width`, `height`, `scale`, and `rotation`
   - `fill`, `outline`, and `opacity`
   - `selected`, `disabled`, and `highlight`
   - `shadow` and restrained `glow`
   - `label` and an `AssetSpec.description`
5. Ensure Diagram mode does not depend on gradients or shadows.
6. Add structural tests to `tests/test_scientific_assets.py`. Update the semantic golden only when the contract change is intentional.

Python configuration example:

```python
asset = AssetSpec(
    AssetKind.BLOCK,
    x=120,
    y=180,
    width=64,
    height=42,
    label="Mass A",
    description="A 2 kg block resting on a 30 degree ramp.",
    style=AssetStyle(selected=True, shadow=True),
)
```

Scene example:

```javascript
PhysicsAssets.block(ctx, frame, {
  x, y, width: 64, height: 42,
  fill: PhysicsVisuals.token(frame, 'colors', 'energy', '#B45309'),
  label: 'Mass A', highlight: true, shadow: true
});
```

## Styling a new simulation

Keep the public builder small and compatible with the simulation manifest:

1. Run the existing typed model in Python.
2. Serialize existing tracks or renderer-neutral geometry.
3. Call `build_player_document()` with a deterministic seed, accessible label, logical dimensions, and scene adapter.
4. Begin the scene with `PhysicsExperience.context()`. Context is a background layer only.
5. Compose the figure with `PhysicsAssets`, `PhysicsAnnotations`, and `PhysicsAnimation`.
6. Use `PhysicsVisuals.responsive(frame)` to reduce nonessential labels on mobile while retaining identifiers and measurements.
7. Render analysis figures through `render_chart()` and `chart_system.py`.
8. Preserve Explore, Compare, Analyze, and Model modes, notebook recording/restoration, missions, badges, profiles, registry navigation, and typed public results.

Do not add a new animation loop. Every simulation uses the shared player's `requestAnimationFrame` lifecycle.

## Schematic versus scaled visuals

Every scientific vector declares a `VectorScaleMode`:

- `PHYSICAL`: displayed length is magnitude × `pixels_per_unit`. Units and a positive scale are mandatory.
- `NORMALIZED`: direction is physical, but length is adjusted for visibility. A disclosure is automatic.
- `SCHEMATIC`: direction is explanatory only. The UI automatically says it is not drawn to scale.

```python
velocity = VectorSpec(
    x=100, y=160, dx=3, dy=4,
    role="velocity",
    scale_mode=VectorScaleMode.PHYSICAL,
    pixels_per_unit=8,
    units="m/s",
)
```

Never let an arbitrary arrow length imply magnitude. Dimension lines, rulers, path guides, normal lines, angle markers, and centers of mass should use `PhysicsAnnotations`. Decorative easing must not be applied to recorded measurements.

## Dark mode

The default visual theme is `auto`, which follows `prefers-color-scheme`. Learners may explicitly choose light or dark mode. Both token payloads are embedded in each player document.

- Read colors through CSS variables or `PhysicsVisuals.token()`.
- Do not inspect browser theme inside an individual scene.
- Do not hard-code a light background behind dark-theme text.
- Validate new foreground/background pairs with `contrast_ratio()`.
- High-contrast accessibility mode remains separate from ordinary dark mode.

## Reduced motion

Reduced motion may come from the saved setting or `prefers-reduced-motion`.

When enabled:

- autoplay is disabled;
- particles, motion blur, impact ripples, collision flashes, and animated camera transitions are disabled;
- manual play, pause, restart, frame stepping, speed control, and scrubbing remain available;
- the final physical state and all measurements remain accessible.

Do not remove model-driven changes merely because reduced motion is active. Present them through manual stepping, scrubbing, or a static final state.

## Presentation levels

### Diagram

Use for maximum clarity: flat fills, strong outlines, minimal environmental detail, and complete scientific annotations. Diagram mode must be sufficient on its own.

### Illustrated

The default. Adds restrained gradients, highlights, shadows, and polished objects without changing geometry or scale.

### Contextual

Optional real-world setting behind the scientific scene. Current contexts include a projectile field, laboratory, space, optics bench, roller-coaster setting, and collision track. Context must never cover vectors, measurements, equations, controls, or labels.

Call:

```javascript
PhysicsExperience.context(ctx, frame, 'laboratory');
// Draw all scientific objects and annotations afterward.
```

## Animation and performance

- Use precomputed immutable tracks; never recompute numerical integration in JavaScript.
- Use the shared `requestAnimationFrame` player and stable display timestep.
- Keep scene drawing proportional to visible objects and bounded trail lengths.
- Use `PhysicsAnimation.fadingTrail()` rather than accumulating unbounded paths.
- Motion blur is optional and capped at four samples.
- Cap dense fields and particles before serialization. Reuse the repository's computational budgets.
- Avoid rebuilding gradients, filtered arrays, and scale extrema inside hot loops when they can be prepared once.
- Keep DPR bounded; the player currently caps it at 2.5.
- Do not attach scene-level global listeners. Player listeners and observers have explicit cleanup.
- Use deterministic seeds for decorative randomness and include the seed in the payload.
- Prefer Canvas 2D and browser-native controls. Do not introduce a game engine for presentation effects.

## Accessibility

- Give every player a concise, meaningful `accessible_label`.
- Provide textual outcomes and chart descriptions outside the canvas.
- Use labels, line styles, shapes, or symbols in addition to color.
- Keep essential labels legible at mobile widths; hide only redundant decoration.
- Maintain a minimum 44 px target for controls.
- Preserve keyboard play/pause, replay, stepping, speed, and scrub behavior.
- Use automatic disclosures for normalized and schematic vectors.
- Support large text, high contrast, dark mode, and reduced motion independently.
- Avoid translucent text and low-contrast grid lines.
- State units on axes, measurements, vector scales, and result summaries.

## Pilot examples

The original pilots now serve as completed migration examples for the full visual system.

- `subjects/mechanics/cannonball/scene.py`: shared cannon/projectile assets, fading trajectory, responsive labels, field context.
- `subjects/waves_and_oscillations/pendulum/scene.py`: shared pivot/cable/bob assembly, fading trail, laboratory context.
- `subjects/mechanics/orbital_gravity/scene.py`: shared star/planet assets, bounded orbital trail, space context.
- `subjects/mechanics/bumper_cars/scene.py`: shared carts, collision ripple/flash, comparison lanes, collision-track context.
- `canvas/ray_diagram.py`: shared lens/ray assets, normal annotation, optics-bench context.
- `subjects/light_and_electricity/thin_lenses/page.py`: analysis routed through the shared chart system.
- `subjects/mechanics/canvas.py`: shared ramp, lever, center-of-mass, rotation, and model-faithful coaster compositions.
- `subjects/waves_and_oscillations/boing/scene.py`, `subjects/waves_and_oscillations/double_pendulum/scene.py`, and `subjects/mechanics/earth_tunnel/scene.py`: recorded oscillation and gravity tracks with bounded trails and explicit diagnostics.
- `canvas/scalar_field.py` and `canvas/wavefronts.py`: fixed-scale wave graphs and physically positioned Doppler wavefronts.
- `canvas/diffusion_player.py`: immutable seeded paths with bounded display work and a statistical RMS guide.

These are composition examples, not licenses to copy simulation-specific constants. Move repeated patterns into the shared library.

## Migration guide for remaining simulations

There are no remaining simulations in the original registry; this guide now applies to future additions and any external compatibility simulation.

Migrate one visual family at a time. A migration should be reviewable and must not combine physics changes with presentation changes.

### Stage 1: establish the baseline

1. Run the relevant model, page, canvas, mission, notebook, and registry tests.
2. Record the current public builder signature, payload shape, accessible description, modes, controls, and comparison behavior.
3. Identify whether each visual quantity is physical, normalized, or schematic.

### Stage 2: migrate scene composition

1. Preserve the existing Python physics result and animation tracks.
2. Replace local circles, rectangles, springs, arrows, and trails with shared assets.
3. Replace local colors, fonts, strokes, radii, shadows, and timing constants with tokens.
4. Replace local arrows and geometry annotations with `PhysicsAnnotations`.
5. Add responsive label behavior and all three presentation levels.
6. Add context only after Diagram and Illustrated modes are complete.

### Stage 3: migrate analysis presentation

1. Keep plotted arrays unchanged.
2. Route Matplotlib figures through `render_chart()`.
3. Use `series_figure()` for simple analysis charts that currently have isolated styling.
4. Retain accessible descriptions, axes, units, legends, line styles, and markers.

### Stage 4: verify preservation

Confirm all of the following before declaring a migration complete:

- numerical result arrays and units are unchanged;
- Explore, Compare, Analyze, and Model all render;
- notebook capture, comparison, pinning, and setup restoration still work;
- missions and badges still evaluate only at their intended action;
- profile and navigation state remain compatible;
- public builder functions and manifest entrypoints remain stable;
- Diagram, Illustrated, Contextual, dark, high-contrast, large-text, and reduced-motion paths remain understandable;
- narrow layouts do not overflow;
- deterministic inputs produce deterministic documents;
- focused and full test suites pass.

The original 22-simulation registry has completed this migration. Apply the same staged process to any future simulation or newly introduced renderer family.

## Completion audit

All 22 registered simulations now declare a `shared-*` renderer and compose their figures through the shared player. The completed set is:

| Family | Simulations |
|---|---|
| Mechanics and gravity | Cannonball, Pendulum, Planet Launcher, Bumper Cars, Inclined Plane, Torque and Levers, Center of Mass, Roller-Coaster Energy, Rotational Motion, Double Pendulum, Earth Tunnel |
| Waves and oscillation | Boing Machine, Wave Interference, Doppler Effect |
| Light and electricity | Reflection and Refraction, Thin Lenses, Electric Fields, Magnetic Forces |
| Fluids and matter | Buoyancy, Fluid Pressure, Gas Laws, Diffusion |

Completion guarantees and audit decisions:

- Scene adapters consume immutable model arrays and use `build_player_document()`; physics and units remain model-owned.
- All vector-like Canvas calls route through `PhysicsAnnotations` with physical, normalized, or schematic semantics. Rays and torque arcs use explicit scene disclosures because their visible lengths are not quantitative vectors.
- Analysis views use `render_chart()`; `st.pyplot()` exists only inside that common renderer. There are no native Streamlit line or bar charts in simulation pages.
- Light and dark semantic colors meet WCAG 2.1 graphical-object contrast of at least 3:1 against their canvas. Primary and muted text retain at least 4.5:1.
- Responsive behavior is owned by the shared player at representative mobile (360 px), tablet (768 px), and desktop (1100 px) widths. Scenes may suppress redundant labels but not scientific identifiers or units.
- Reduced motion disables autoplay and decorative effects while retaining scrub and frame-step controls. High contrast, large text, explicit light/dark themes, and automatic theme selection are serialized into every player.
- Context is drawn before scientific assets and annotations. Diagram mode therefore remains complete, while Contextual scenery cannot cover the scientific overlay.
- `canvas/embed.py` is the canonical Streamlit `show()` adapter; the completed legacy re-export has
  been removed.

The few remaining hexadecimal values inside scene sources are defensive fallbacks passed to semantic token lookups, plus deterministic decorative particle-burst colors. They are not independent scene palettes and do not encode quantitative meaning. Specialized target rings and field glyphs remain scene compositions because they are not repeated asset concepts.

If a migration exposes a physics defect, document it and fix it in a separate change with model-level tests. Do not conceal a numerical change inside visual work.

## Tests

Focused visual checks:

```bash
python -m pytest -q \
  tests/test_visual_system.py \
  tests/test_scientific_assets.py \
  tests/test_vector_annotations.py \
  tests/test_animation_presentation.py \
  tests/test_presentation_levels.py \
  tests/test_visual_pilots.py \
  tests/test_visual_regression.py
```

Always finish a migrated simulation with the complete suite:

```bash
python -m pytest -q
```
