# Educational visual accuracy audit

This audit treats recorded model results as authoritative. Presentation code may clarify those
results, but it must not alter physics to match a drawing.

## Scale rules

- A `physical` vector uses vector components in the declared unit and one positive
  `pixels_per_unit` value. Display length is `magnitude × pixels_per_unit`, with zero intercept.
- A set of physically scaled forces uses one shared scale and renders a reference segment labeled
  with its force magnitude.
- A `normalized` vector preserves direction but adjusts length for visibility. Its canvas must say
  so.
- A `schematic` vector communicates a convention or direction only and must say it is not to scale.
- A resultant shown beside its component forces is dashed and labeled as a resultant so it is not
  mistaken for an additional interaction.

## Findings and disposition

| Area | Finding | Disposition |
| --- | --- | --- |
| Inclined plane | Labeled force arrows used a nonzero length offset, so force ratios were not linear. | Corrected to a shared zero-intercept N-to-pixel scale with an on-canvas reference legend. |
| Inclined plane | Static and kinetic friction were both labeled only “friction.” | Labels and callout now name the active regime, maximum static friction, and slip angle. The Model panel discloses the idealized instantaneous transition. |
| Inclined plane | Net force could look like an additional applied force. | It is now labeled “resultant,” drawn dashed, and explained below the diagram. |
| Pendulum | The small-angle model could be selected at visibly large angles without a quantitative warning. | The page now states `sin(theta) ≈ theta`, reports the current period discrepancy, and recommends the nonlinear model above 15 degrees. The model remains selectable for comparison. |
| Spring oscillator | Displacement uses a documented physical m-to-pixel mapping. Velocity and restoring force are normalized. | Existing shared disclosure is accurate; no physics change required. |
| Lever, buoyancy, fluid pressure, Earth tunnel, and field diagrams | Several arrows are intentionally normalized because simultaneous quantities or responsive bounds make a common quantitative scale impractical. | Existing normalized/schematic disclosures remain mandatory. Follow-up migrations should use physical scaling only when all arrows share a meaningful unit and scale. |
| Speed and duration comparisons | Reference objects and activities had variable, unsourced values. | Removed from compatibility formatters. Copy now reports SI values and exact `km/h`, minute, and hour conversions. |

## Idealization and units

The inclined-plane model assumes a rigid block and ramp, constant coefficients, no deformation or
air drag, and an instantaneous switch from static to kinetic friction. The pendulum model assumes a
point bob, rigid massless rope, fixed support and gravity, and no drag or pivot friction. These are
model boundaries, not claims about all real systems.

Force labels use newtons, acceleration uses metres per second squared, speed uses metres per
second, angles use degrees in controls and radians inside trigonometric calculations, and elapsed
time uses seconds in simulation results. Conversion copy is covered by unit tests.

## Review checklist

When adding or migrating a diagram:

1. Identify whether each visible quantity is physical, normalized, or schematic.
2. For physical vectors, test linearity and units and draw a scale legend where meaningful.
3. For normalized or schematic vectors, include an on-canvas disclosure.
4. State idealizations and transitions that could create a misconception.
5. Test deterministic geometry and add only a representative perceptual baseline.
