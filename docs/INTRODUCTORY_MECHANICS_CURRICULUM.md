# Introductory Mechanics curriculum roadmap

## Course boundary

This roadmap defines the first coherent Physics Studio course for advanced high-school through
first-semester undergraduate learners. It contains eight units and 24 lessons (about 22–24 class
hours including cumulative work). Algebra, trigonometry, graph interpretation, and optional
calculus-level reasoning are developed in context. The standard path is algebra based; lessons
marked **standard + extended** include derivation or numerical-analysis extensions.

This is a curriculum specification, not authored lesson prose or an active UI catalog. The
machine-readable source is
`physics_playground/subjects/mechanics/course_roadmap.py`. Its validator checks unique IDs,
forward-only prerequisite edges, objective references from assessments, durations, mathematical
depths, and registered simulation IDs.

Every lesson includes a worked example, at least one conceptual assessment and one quantitative or
cumulative assessment, misconception diagnostics, and explicit mastery evidence. A simulation is
used only when the existing model materially supports the objective.

## Unit 1 — Measurement, models, vectors, and graphs

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m01-measurement-models` — Measurement, units, uncertainty, and models | None | Convert to coherent SI units and report sensible precision; distinguish systems, assumptions, idealizations, and limits. Concepts: dimensions, uncertainty, models. Standard. | Estimate walking speed from distance/time with uncertainty. No simulation. | Conceptual: identify an assumption. Quantitative: compound-unit conversion and dimensional check. Diagnose “more decimals means more accuracy” and “a model copies reality.” | 50 min. Mastery: dimensionally valid result with justified precision plus a system-model-limit statement. |
| `m02-vectors-coordinates` — Coordinates, scalars, and vectors | `m01-measurement-models` | Choose a coordinate system; resolve and recombine vectors. Concepts: scalars, vectors, components, signs. Standard. | Resolve a 12 m displacement at 35° and reconstruct it. No simulation. | Conceptual sign choice; quantitative components/resultant. Diagnose “negative component means negative magnitude.” | 50 min. Mastery: labeled component diagram and reconstruction of the original vector. |
| `m03-motion-graphs` — Reading motion graphs | `m02-vectors-coordinates` | Interpret slope and signed area; translate among stories, tables, and motion graphs. Concepts: position, velocity, acceleration, slope, area. Standard. | Infer motion and displacement from a piecewise position-time graph. No simulation. | Match story to graph; calculate slopes and signed areas. Diagnose “graph height always means speed” and “negative velocity means slowing.” | 50 min. Mastery: annotated graph and correct signed displacement. |

## Unit 2 — One-dimensional motion

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m04-average-instantaneous` — Average and instantaneous motion | `m03-motion-graphs` | Calculate interval-average velocity/acceleration; explain instantaneous velocity as limiting slope and distinguish it from average speed. Standard. | Compare speed and velocity for a round trip. No simulation. | Explain zero round-trip average velocity; calculate averages from position data. Diagnose speed/velocity interchange. | 50 min. Mastery: correct interval results and secant-to-tangent explanation. |
| `m05-constant-acceleration` — Constant-acceleration models | `m04-average-instantaneous` | Derive relations from graph slope/area; select and apply a relation with consistent intervals. Standard + extended. | Find braking stopping distance. No simulation. | Select an equation from knowns/unknowns; solve and validate a braking problem. Diagnose mixed time intervals and “zero velocity means zero acceleration.” | 50 min. Mastery: graph-based derivation and checked stopping distance. |
| `m06-free-fall-review` — Free fall and one-dimensional synthesis | `m05-constant-acceleration` | Model vertical motion with a stated sign convention; synthesize graph, equation, units, and limiting cases. Standard. | Find launch speed and total flight time for a vertical throw. No simulation. | Diagnose acceleration at the top; cumulative two-stage vertical problem. Diagnose “heavier falls faster.” | 50 min. Mastery: signed solution with agreement across representations. |

## Unit 3 — Two-dimensional and projectile motion

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m07-vector-kinematics` — Two-dimensional kinematics | `m02-vectors-coordinates`, `m05-constant-acceleration` | Apply kinematics on perpendicular axes; reconnect components through shared time. Standard. | Aircraft displacement with crosswind. No simulation. | Identify component coupling; calculate displacement and direction. Diagnose “components happen at different times.” | 50 min. Mastery: component table with shared time and reconstructed trajectory displacement. |
| `m08-projectile-components` — Projectile motion from components | `m07-vector-kinematics`, `m06-free-fall-review` | Derive level-ground flight time/range; compare analytic predictions with evidence and assumptions. Standard + extended. | Range and peak height for 20 m/s at 45°. Cannonball Compare: complementary angles, then ideal versus drag. | Explain complementary ranges; predict range/time/height. Diagnose sustained forward force and universal 45° maximum. | 60 min. Mastery: predictions within tolerance plus claim-evidence-limit comparison. |
| `m09-projectile-applications` — Projectile applications and kinematics review | `m08-projectile-components` | Solve unequal-height problems; validate with units, limiting cases, and applicable simulation evidence. Standard + extended. | Launch from a platform. Cannonball Analyze provides a level-ground limiting-case audit, explicitly not an unequal-height model. | Select physical quadratic root; unfamiliar cumulative 2-D problem. Diagnose “every algebraic root is physical.” | 60 min. Mastery: justified physical root, trajectory, and validation checklist. |

## Unit 4 — Forces and free-body diagrams

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m10-interactions-newton` — Interactions and Newton’s laws | `m06-free-fall-review` | Identify forces as interactions and distinguish mass/weight; apply Newton’s laws and interaction pairs. Standard. | Two pushed blocks and their contact forces. No simulation. | Identify a third-law pair; calculate acceleration from force inventory. Diagnose “action-reaction cancels on one object” and “motion requires net force.” | 50 min. Mastery: correct boundaries/pairs and net-force calculation. |
| `m11-free-body-diagrams` — Free-body diagrams and force models | `m10-interactions-newton`, `m02-vectors-coordinates` | Construct an object-centered diagram without nonforces; translate it into component equations. Standard. | Suspended sign with two cables. No simulation. | Repair a diagram containing velocity; solve its force equations. Diagnose “normal always equals weight.” | 50 min. Mastery: complete diagram with equations traceable to arrows. |
| `m12-friction-inclines` — Friction and inclined planes | `m11-free-body-diagrams` | Distinguish static/kinetic friction and direction; calculate slipping threshold and acceleration. Standard + extended. | Minimum slipping angle. Inclined Plane Compare: bracket threshold and compare surfaces. | Determine whether static friction is maximal; predict threshold and acceleration. Diagnose `f_s = μ_sN` as an equality in every case. | 60 min. Mastery: correct threshold inequality and simulation bracket. |

## Unit 5 — Work and energy

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m13-work-kinetic-energy` — Work and the kinetic-energy theorem | `m12-friction-inclines` | Calculate signed work including force angle; apply work-energy to a defined system. Standard. | Frictional stopping distance by energy. No simulation. | Determine work signs; compare energy and kinematics solutions. Diagnose “any applied force does positive work.” | 50 min. Mastery: signed work inventory and equivalent solutions. |
| `m14-potential-conservation` — Potential energy and conservation | `m13-work-kinetic-energy` | Define gravitational potential energy and reference; predict speed and reachable position using conservation. Standard. | Coaster speed and maximum height. Roller Coaster Analyze: energy graphs. | Explain arbitrary potential zero; calculate speeds/turning points. Diagnose “potential energy belongs to one object” and “conservation means kinetic energy is constant.” | 60 min. Mastery: consistent system/reference and predictions matching ideal metrics. |
| `m15-dissipation-energy-review` — Dissipation, power, and energy review | `m14-potential-conservation` | Track energy transfers when mechanical energy changes; choose among force, kinematics, and energy methods. Standard + extended. | Minimum launch energy for a lossy coaster. Roller Coaster Compare: ideal versus dissipative. | Locate energy outside mechanical account; solve one motion by two methods. Diagnose “lost energy disappears.” | 50 min. Mastery: complete energy account and justified method comparison. |

## Unit 6 — Momentum and collisions

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m16-impulse-momentum` — Impulse and momentum | `m10-interactions-newton`, `m13-work-kinetic-energy` | Relate impulse to momentum change; choose a system where external impulse is negligible. Standard. | Triangular force-time pulse. No simulation. | Choose a conservation system; calculate signed graph area. Diagnose “momentum is conserved for each object” and impulse/force unit confusion. | 50 min. Mastery: justified boundary and impulse equal to momentum change. |
| `m17-collision-models` — Elastic and inelastic collisions | `m16-impulse-momentum` | Apply momentum conservation; use kinetic energy and restitution to classify collisions. Standard + extended. | Equal-mass elastic and sticking collisions. Bumper Cars Compare: matched restitution cases. | Distinguish conserved momentum from kinetic energy; predict final velocities and energy change. Diagnose “objects that stick must stop.” | 60 min. Mastery: momentum closure and evidence-based classification. |
| `m18-momentum-synthesis` — Collision synthesis and review | `m17-collision-models` | Solve multistage collision/motion problems; defend conservation claims by system and interval. Standard + extended. | Ballistic-pendulum-style collision plus energy conversion. Bumper Cars Analyze audits calculations. | Select law by stage; cumulative checked solution. Diagnose “one conservation equation applies unchanged across every stage.” | 60 min. Mastery: stage diagram and quantitative synthesis. |

## Unit 7 — Rotation, torque, and center of mass

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m19-angular-kinematics` — Angular kinematics and rotational inertia | `m05-constant-acceleration`, `m14-potential-conservation` | Connect angular and linear variables; predict effects of mass distribution on response and energy. Standard + extended. | Disk versus hoop under equal torque. Rotational Motion Compare. | Rank bodies by inertia; calculate angular motion. Diagnose “inertia depends only on mass.” | 60 min. Mastery: analogy table and simulation-backed shape prediction. |
| `m20-torque-equilibrium` — Torque, levers, and static equilibrium | `m11-free-body-diagrams`, `m19-angular-kinematics` | Calculate torque from lever arm/direction; apply force and torque equilibrium together. Standard + extended. | Loaded beam supports. Torque and Levers Analyze. | Compare equal forces at different arms/angles; solve equilibrium. Diagnose “larger force always means larger torque.” | 60 min. Mastery: lever-arm diagram and simultaneous balances. |
| `m21-center-mass-rotation-review` — Center of mass and rotational synthesis | `m20-torque-equilibrium` | Calculate and interpret center of mass; combine center of mass, force, torque, and energy. Standard. | Three point masses and balancing pivot. Center of Mass Compare. | Predict shifts; cumulative balance problem. Diagnose “center of mass must be inside” and “geometric center always matches.” | 60 min. Mastery: verified weighted average and torque-supported balance prediction. |

## Unit 8 — Gravitation, orbital motion, and synthesis

| Lesson | Prerequisites | Objectives and concepts | Required example and activity | Assessment and misconceptions | Duration and mastery evidence |
| --- | --- | --- | --- | --- | --- |
| `m22-universal-gravitation` — Universal gravitation and gravitational energy | `m14-potential-conservation`, `m02-vectors-coordinates` | Apply inverse-square force with direction; connect force, field, potential energy, and escape energy. Standard + extended. | Surface gravity and escape speed for a planet. No simulation. | Predict inverse-square changes; calculate force/energy/escape speed. Diagnose “orbit means no gravity” and universal use of `mgh`. | 50 min. Mastery: correct ratios and checked escape calculation. |
| `m23-orbits` — Circular, elliptical, and escape trajectories | `m22-universal-gravitation`, `m08-projectile-components` | Explain orbit as free fall and calculate circular conditions; distinguish impact, bound, and escape paths using energy/angular-momentum evidence. Standard + extended. | Circular speed and period. Planet Launcher Compare: impact, elliptical, circular, escape. | Explain no-thrust ideal orbit; classify from launch speed and energy. Diagnose “centripetal force is extra” and “orbit requires engine thrust.” | 65 min. Mastery: circular-speed prediction and evidence-backed trajectory taxonomy. |
| `m24-mechanics-synthesis` — Introductory Mechanics cumulative synthesis | `m18-momentum-synthesis`, `m21-center-mass-rotation-review`, `m23-orbits` | Connect kinematic, force, momentum, energy, and rotational representations; construct and critique a model. Standard + extended. | Staged launch-and-collision scenario using three frameworks. Cannonball Model audits an earlier notebook run. | Defend law/representation by stage; cumulative multirepresentation problem. Diagnose “the most advanced equation is always best” and “one matching result proves all assumptions.” | 75 min. Mastery: coherent course-wide solution map and claim-evidence-assumptions-limitations defense. |

## Simulation allocation and known gaps

The roadmap uses eight existing Mechanics simulations: Cannonball, Inclined Plane, Roller-Coaster
Energy, Bumper Cars, Rotational Motion, Torque and Levers, Center of Mass, and Planet Launcher.
They are evidence tools, not substitutes for derivation or problem solving.

No existing simulation is assigned where it would distort the lesson. The principal non-simulation
content gaps are:

- measurement uncertainty, unit conversion, and experimental graph construction;
- general one-dimensional motion and free fall;
- vector addition independent of projectile motion;
- interaction diagrams and reusable free-body-diagram practice;
- force-time/impulse graph construction;
- general gravitational field and potential visualization;
- integrated multistage problem workspace and assessment feedback.

These gaps require authored diagrams, datasets, worked examples, practice, and assessments first.
They do not justify adding simulations by default.

The existing Earth Tunnel simulation is valuable but depends on interior-density models and simple
harmonic motion beyond the core gravitation sequence. Oscillations likewise fit a follow-on unit or
course extension, not the required 24-lesson spine. Orbital Gravity supplies the core course's
gravitation synthesis without pulling oscillations into scope.

## Implementation boundary

Before activation in the curriculum catalog, each roadmap lesson must be expanded into the current
typed `Lesson` components: full coordinate choices, laws, derivations, units, validation, limiting
cases, model limitations, worked substitutions, checkpoint answer keys, activity presets, and
accessible diagrams. Non-simulation lessons also require the active curriculum model to stop
requiring a simulation activity; that change should be made as an explicit domain invariant, not
worked around with unrelated simulations.
