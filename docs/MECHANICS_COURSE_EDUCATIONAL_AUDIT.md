# Mechanics course educational audit

Audited 2026-07-18 against the five implemented lessons. The longer curriculum roadmap
is a plan, not learner-visible course content, and was not scored as though it were taught.
The review used three lenses: physics educator (accuracy and mathematical coherence),
instructional designer (alignment and progression), and skeptical student (clarity,
workload, and whether an activity can actually support its claim).

## Course-level findings

The prerequisite and next-step chain is forward and coherent: models and measurement → signed motion
quantities → linked motion graphs → constant acceleration → projectile motion. The largest
gap was vector decomposition: it was both an objective and a declared prerequisite of the
projectile lesson. It is now taught in that lesson, while right-triangle trigonometry is
stated honestly as the prerequisite skill. Lesson 1's formerly stale next-step ID and title
now route to the implemented Lesson 2.

The course consistently asks for predictions, controlled comparisons, units, and model
limitations. Simulation completion alone is not mastery. However, several checkpoints
sampled only easy verbal recognition while their objectives promised graph translation,
derivation, or numerical application. Numeric acceleration, stopping-distance, component,
and model-limit checkpoints now provide independent evidence for those claims. The
constant-acceleration relations now have an explicit graph-based derivation with assumptions,
unit validation, and a validity boundary.

Reading demand is appropriate for advanced high-school or first-semester undergraduate
learners, but symbol-dense derivations still require equation narration and screen-reader
checking. Every simulation activity should be treated as evidence only when its requested
record includes a prediction or question, controlled observations, and reasoning.

## Lesson-by-lesson audit

### M01 — Models, Measurements, and Representations

- **Teaches:** system versus model, quantities and units, precision versus accuracy,
  introductory uncertainty, variables, graphs and diagrams, and simulation versus experiment.
- **Evidence:** system/model checkpoint, resolution checkpoint, numeric graph reading, two
  controlled range observations, and a claim–evidence–limitation reflection.
- **Likely misconceptions:** model as perfect copy, displayed digits as accuracy, graph as
  trajectory, and control manipulation as scientific reasoning.
- **Prerequisites:** arithmetic, ratios, and reading axes; these are reasonable entry skills.
- **Unnecessary or overloaded content:** projectile details are examples, not assumed knowledge;
  the learner should not be asked to explain projectile physics here.
- **Misleading language corrected:** simulation output is reproducible within numerical
  precision, not “exact.” The prediction now explicitly precedes running the simulation.
- **Assessment weakness remaining:** uncertainty propagation is demonstrated but not graded;
  this is acceptable because the objective asks for introductory reporting, not formal error
  analysis.

### M02 — Position, Displacement, Velocity, and Speed

- **Teaches:** origins, positive direction, signed position/displacement/velocity, path distance,
  and average speed.
- **Evidence:** endpoint and path calculations, a lap misconception checkpoint, and a walking-route
  transfer requiring all four quantities with units.
- **Likely misconceptions:** distance equals displacement, speed can be negative, and negative
  velocity means slowing.
- **Prerequisites:** M01 plus signed arithmetic. Signed arithmetic should be remediated locally if
  needed rather than treated as completed physics content.
- **Unnecessary content:** collision dynamics are not part of the objective and should not be
  inferred from the Bumper Cars context.
- **Misleading activity corrected:** the collision simulation cannot enact the imagined round
  trip. The activity now identifies it as a thought experiment and uses the simulation only as
  a coordinate-track context.
- **Assessment weakness:** the selected checkpoint is recognition-level; the required transfer
  response supplies the quantitative evidence the checkpoint alone lacks.

### M03 — Velocity, Acceleration, and Motion Graphs

- **Teaches:** slope and signed area links among position, velocity, and acceleration; velocity
  versus acceleration at an instant; and sign-based speeding/slowing reasoning.
- **Evidence:** linked graph explanation with intervals and units, numeric average acceleration,
  direction checkpoint, and transfer to a braking vehicle.
- **Likely misconceptions:** zero velocity implies zero acceleration, negative velocity means
  slowing, acceleration follows motion, and a motion graph pictures the spatial path.
- **Prerequisites:** M02 and informal slope/area interpretation. Formal calculus is not required.
- **Cognitive load:** Cannonball previews two-dimensional motion, but the task explicitly isolates
  the vertical component; projectile range physics is not required.
- **Visual risk:** learners may confuse the trajectory with position–time graphs. Axis labels,
  graph descriptions, and the prompt must remain visible together.
- **Assessment weakness fixed:** the original sign-only item did not demonstrate the promised
  numerical acceleration or graph link. A signed numeric acceleration checkpoint now does.

### M05 — Constant-Acceleration Reasoning

- **Teaches:** deriving velocity and displacement relations from slope and area, eliminating time,
  choosing equations from known quantities, and testing model assumptions.
- **Evidence:** a four-step derivation, stopping-distance example and numeric checkpoint, sign
  checkpoint, controlled incline comparison, and transfer to projectile components.
- **Likely misconceptions:** formulas are unrelated rules, greater gravitational force guarantees
  greater acceleration, heavier objects fall faster, and acceleration follows motion.
- **Prerequisites:** M03, algebraic rearrangement, signed area, and squaring signed quantities.
- **Unnecessary content:** detailed force analysis is limited to explaining why mass cancels; a
  full forces unit is not presumed.
- **Scientific boundary:** equations apply during an interval of constant acceleration, not to
  every trajectory or an entire braking event with changing acceleration.
- **Assessment weakness fixed:** a qualitative sign question was incorrectly labeled as evidence
  for derivation. It now assesses application; a new numeric item assesses use of the derived
  time-independent relation.

The `M05` identifier preserves the curriculum roadmap's stable IDs; the absence of an implemented
M04 is a numbering gap, not a hidden prerequisite.

### Projectile Motion from Components

- **Teaches:** velocity decomposition, independent component evolution linked by time, the
  level-ground range derivation, complementary angles, validation, and ideal-model limits.
- **Evidence:** numeric horizontal-component checkpoint, prediction and three-angle observations,
  complementary-angle comparison, derivation and range checkpoint, drag comparison, explicit
  model-limit checkpoint, and reflection.
- **Likely misconceptions:** a forward sustaining force is required, gravity turns off at the
  apex, heavier projectiles fall faster, complementary angles have identical trajectories, and
  45° always maximizes range.
- **Prerequisites corrected:** constant-acceleration reasoning and right-triangle trigonometry.
  Vector decomposition is no longer circularly listed as prior knowledge because it is taught and
  assessed here. Quadratic-root selection remains an explicit algebra skill.
- **Cognitive load:** component calculation precedes the full range derivation; drag and numerical
  integration remain a clearly marked extension.
- **Visual/language risks:** trajectory height and range share spatial axes, while time graphs do
  not; line labels and patterns must carry meaning without color. “Independent” components still
  share the same time and termination event.
- **Assessment weaknesses fixed:** range symmetry was previously the only automatically graded
  objective. Component calculation and recognition of a changed physical assumption now cover
  the other objectives without pretending that a multiple-choice answer alone proves mastery.

## Remaining manual review

Automated validation can confirm references, units, answer keys, progression, serialization, and
lesson flow. It cannot establish reading comprehension, screen-reader intelligibility of spoken
equations, whether hints reveal too much, or whether real learners transfer the ideas. Those need
think-aloud sessions with target learners, including keyboard and screen-reader users. This audit
does not claim instructional effectiveness from implementation inspection alone.
