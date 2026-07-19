"""Machine-readable skeleton for the proposed Introductory Mechanics course.

This is planning data, not the active lesson catalog. It intentionally stops before
full lesson prose, UI routing, parameter presets, and scored answer keys.
"""

from __future__ import annotations

from dataclasses import dataclass

from physics_playground.education.audience import MathematicalDepth
from physics_playground.models.simulations import LearningMode
from physics_playground.validation import PhysicsValidationError


@dataclass(frozen=True, slots=True)
class RoadmapObjective:
    id: str
    statement: str


@dataclass(frozen=True, slots=True)
class RoadmapActivity:
    simulation_id: str
    mode: LearningMode
    task: str
    evidence: str


@dataclass(frozen=True, slots=True)
class RoadmapAssessment:
    kind: str
    prompt_specification: str
    objective_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RoadmapLesson:
    id: str
    title: str
    prerequisite_lesson_ids: tuple[str, ...]
    objectives: tuple[RoadmapObjective, ...]
    core_concepts: tuple[str, ...]
    mathematical_depths: frozenset[MathematicalDepth]
    worked_examples: tuple[str, ...]
    simulation_activities: tuple[RoadmapActivity, ...]
    assessments: tuple[RoadmapAssessment, ...]
    misconceptions: tuple[str, ...]
    estimated_minutes: int
    mastery_evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RoadmapUnit:
    id: str
    title: str
    lessons: tuple[RoadmapLesson, ...]


def objective(lesson_id: str, number: int, statement: str) -> RoadmapObjective:
    return RoadmapObjective(f"{lesson_id}-o{number}", statement)


def lesson(
    lesson_id: str,
    title: str,
    prerequisites: tuple[str, ...],
    objective_statements: tuple[str, str],
    concepts: tuple[str, ...],
    example: str,
    assessments: tuple[tuple[str, str, tuple[int, ...]], ...],
    misconceptions: tuple[str, ...],
    mastery: tuple[str, ...],
    *,
    activity: RoadmapActivity | None = None,
    minutes: int = 50,
    extended: bool = False,
) -> RoadmapLesson:
    objectives = tuple(
        objective(lesson_id, number, statement)
        for number, statement in enumerate(objective_statements, start=1)
    )
    return RoadmapLesson(
        lesson_id,
        title,
        prerequisites,
        objectives,
        concepts,
        frozenset(
            {MathematicalDepth.STANDARD, MathematicalDepth.EXTENDED}
            if extended
            else {MathematicalDepth.STANDARD}
        ),
        (example,),
        (activity,) if activity else (),
        tuple(
            RoadmapAssessment(kind, prompt, tuple(objectives[index - 1].id for index in refs))
            for kind, prompt, refs in assessments
        ),
        misconceptions,
        minutes,
        mastery,
    )


INTRODUCTORY_MECHANICS_UNITS = (
    RoadmapUnit(
        "foundations",
        "Measurement, models, vectors, and graphs",
        (
            lesson(
                "m01-measurement-models",
                "Measurement, units, uncertainty, and models",
                (),
                (
                    "Convert measurements to coherent SI units and report sensible precision.",
                    "Distinguish a physical system from assumptions, idealizations, and model limits.",
                ),
                ("SI units", "dimensions", "uncertainty", "models"),
                "Estimate a walking speed from measured distance and time, including units and uncertainty.",
                (
                    (
                        "conceptual",
                        "Identify the model assumption in a measurement scenario.",
                        (2,),
                    ),
                    (
                        "quantitative",
                        "Convert compound units and check dimensional consistency.",
                        (1,),
                    ),
                ),
                (
                    "More decimal places always mean greater accuracy.",
                    "A model is a miniature copy of reality.",
                ),
                (
                    "A dimensionally valid calculation with justified precision.",
                    "A system-model-limit statement.",
                ),
            ),
            lesson(
                "m02-vectors-coordinates",
                "Coordinates, scalars, and vectors",
                ("m01-measurement-models",),
                (
                    "Choose and state a coordinate system for a mechanics problem.",
                    "Resolve and recombine two-dimensional vectors using components.",
                ),
                ("coordinates", "scalars", "vectors", "components"),
                "Resolve a 12 m displacement at 35 degrees and reconstruct its magnitude and direction.",
                (
                    (
                        "conceptual",
                        "Choose signs for two vectors in a stated coordinate system.",
                        (1,),
                    ),
                    ("quantitative", "Compute components and resultant with units.", (2,)),
                ),
                (
                    "A negative component means a negative magnitude.",
                    "Vector components are independent vectors with unrelated units.",
                ),
                (
                    "A labeled component diagram.",
                    "Component calculations that reconstruct the original vector.",
                ),
            ),
            lesson(
                "m03-motion-graphs",
                "Reading motion graphs",
                ("m02-vectors-coordinates",),
                (
                    "Interpret slope and signed area on position, velocity, and acceleration graphs.",
                    "Translate consistently among verbal, graphical, and tabular motion descriptions.",
                ),
                ("position", "velocity", "acceleration", "slope", "area"),
                "Infer velocity intervals and displacement from a piecewise position-time graph.",
                (
                    ("conceptual", "Match a motion story to a graph and explain the match.", (2,)),
                    (
                        "quantitative",
                        "Calculate slope and signed area over specified intervals.",
                        (1,),
                    ),
                ),
                ("A graph's height always gives speed.", "Negative velocity means slowing down."),
                (
                    "A graph annotation connecting slope/area to physical quantities.",
                    "Correct signed displacement.",
                ),
            ),
        ),
    ),
    RoadmapUnit(
        "kinematics-1d",
        "One-dimensional motion",
        (
            lesson(
                "m04-average-instantaneous",
                "Average and instantaneous motion",
                ("m03-motion-graphs",),
                (
                    "Calculate average velocity and average acceleration over an interval.",
                    "Explain instantaneous velocity as a limiting slope and distinguish it from average speed.",
                ),
                ("average velocity", "instantaneous velocity", "average acceleration"),
                "Compare average speed and average velocity for a round trip.",
                (
                    (
                        "conceptual",
                        "Explain why a round trip can have zero average velocity.",
                        (2,),
                    ),
                    ("quantitative", "Compute interval averages from timestamped positions.", (1,)),
                ),
                ("Average speed and average velocity are interchangeable.",),
                ("Correct interval calculations.", "A secant-to-tangent explanation."),
            ),
            lesson(
                "m05-constant-acceleration",
                "Constant-acceleration models",
                ("m04-average-instantaneous",),
                (
                    "Derive constant-acceleration relations from graph slope and area.",
                    "Select and apply a kinematic relation without mixing incompatible intervals.",
                ),
                ("constant acceleration", "kinematic equations", "initial conditions"),
                "Find stopping distance from initial speed and constant braking acceleration.",
                (
                    (
                        "conceptual",
                        "Select the equation matching known and unknown quantities.",
                        (2,),
                    ),
                    (
                        "quantitative",
                        "Solve a multistep braking problem and validate signs and units.",
                        (1, 2),
                    ),
                ),
                (
                    "The symbol t can refer to different intervals in one equation.",
                    "Zero velocity implies zero acceleration.",
                ),
                (
                    "A derived relation from a velocity graph.",
                    "A validated stopping-distance solution.",
                ),
                extended=True,
            ),
            lesson(
                "m06-free-fall-review",
                "Free fall and one-dimensional synthesis",
                ("m05-constant-acceleration",),
                (
                    "Model near-Earth vertical motion with a stated sign convention and uniform gravity.",
                    "Synthesize graph, equation, and limiting-case evidence for one-dimensional motion.",
                ),
                ("free fall", "gravity", "turning points", "model validation"),
                "Determine launch speed and total flight time for a vertically thrown ball.",
                (
                    (
                        "misconception diagnostic",
                        "Evaluate velocity and acceleration at the top of a throw.",
                        (1,),
                    ),
                    (
                        "cumulative quantitative",
                        "Solve and graph a two-stage vertical-motion problem.",
                        (1, 2),
                    ),
                ),
                (
                    "Acceleration is zero at the top.",
                    "Heavier objects have greater free-fall acceleration.",
                ),
                (
                    "A correctly signed vertical-motion solution.",
                    "Agreement among graph, equation, and limiting cases.",
                ),
            ),
        ),
    ),
    RoadmapUnit(
        "kinematics-2d",
        "Two-dimensional and projectile motion",
        (
            lesson(
                "m07-vector-kinematics",
                "Two-dimensional kinematics",
                ("m02-vectors-coordinates", "m05-constant-acceleration"),
                (
                    "Apply kinematics independently along perpendicular coordinate axes.",
                    "Use shared time to reconnect component motions into a trajectory.",
                ),
                ("component motion", "trajectory", "parametric time"),
                "Find the displacement of an aircraft with constant crosswind.",
                (
                    ("conceptual", "Identify which quantities couple component motions.", (2,)),
                    ("quantitative", "Calculate a two-axis displacement and direction.", (1, 2)),
                ),
                ("Perpendicular components happen at different times.",),
                (
                    "A component table with one shared time interval.",
                    "A reconstructed trajectory displacement.",
                ),
            ),
            lesson(
                "m08-projectile-components",
                "Projectile motion from components",
                ("m07-vector-kinematics", "m06-free-fall-review"),
                (
                    "Resolve launch velocity and derive level-ground flight time and range.",
                    "Compare analytic predictions with trajectory evidence and state model assumptions.",
                ),
                ("projectile motion", "range", "flight time", "idealization"),
                "Calculate the ideal range and peak height of a 20 m/s launch at 45 degrees.",
                (
                    ("conceptual", "Explain equal ranges for complementary angles.", (1,)),
                    (
                        "quantitative",
                        "Predict range, time, and height before running the model.",
                        (1, 2),
                    ),
                ),
                (
                    "A forward force sustains horizontal motion.",
                    "The 45-degree result applies with drag in all cases.",
                ),
                (
                    "Predictions within stated tolerance of the ideal run.",
                    "A claim-evidence-limit comparison.",
                ),
                activity=RoadmapActivity(
                    "cannonball",
                    LearningMode.COMPARE,
                    "Compare complementary angles at fixed speed, then contrast ideal and drag trajectories.",
                    "Notebook runs plus a component-based explanation of range and model limits.",
                ),
                minutes=60,
                extended=True,
            ),
            lesson(
                "m09-projectile-applications",
                "Projectile applications and cumulative kinematics review",
                ("m08-projectile-components",),
                (
                    "Solve projectile problems with unequal launch and landing heights.",
                    "Evaluate a kinematic solution using units, limiting cases, and simulation evidence.",
                ),
                ("unequal heights", "quadratic roots", "kinematics synthesis"),
                "Determine the landing time and horizontal distance for a ball launched from a platform.",
                (
                    (
                        "misconception diagnostic",
                        "Choose the physical root of the vertical equation.",
                        (1,),
                    ),
                    (
                        "cumulative quantitative",
                        "Solve an unfamiliar two-dimensional motion problem.",
                        (1, 2),
                    ),
                ),
                ("Every algebraic time root represents a physical event.",),
                ("A justified physical root and trajectory.", "A complete validation checklist."),
                activity=RoadmapActivity(
                    "cannonball",
                    LearningMode.ANALYZE,
                    "Use graphs to test a hand-calculated level-ground limiting case before discussing unequal heights.",
                    "An annotated comparison distinguishing supported and unsupported geometry.",
                ),
                minutes=60,
                extended=True,
            ),
        ),
    ),
    RoadmapUnit(
        "forces",
        "Forces and free-body diagrams",
        (
            lesson(
                "m10-interactions-newton",
                "Interactions and Newton's laws",
                ("m06-free-fall-review",),
                (
                    "Identify forces as interactions and distinguish mass from weight.",
                    "Apply Newton's laws to relate net force, acceleration, and interaction pairs.",
                ),
                ("force", "mass", "weight", "Newton's laws"),
                "Find acceleration and contact-force pairs for two pushed blocks.",
                (
                    ("conceptual", "Identify a valid Newton's-third-law pair.", (2,)),
                    ("quantitative", "Calculate acceleration from a force inventory.", (1, 2)),
                ),
                ("Action-reaction forces cancel on one object.", "Motion requires a net force."),
                ("Correct system boundaries and interaction pairs.", "A net-force calculation."),
            ),
            lesson(
                "m11-free-body-diagrams",
                "Free-body diagrams and force models",
                ("m10-interactions-newton", "m02-vectors-coordinates"),
                (
                    "Construct a free-body diagram for a chosen system without including nonforces.",
                    "Translate the diagram into component equations with a useful coordinate choice.",
                ),
                ("system boundary", "free-body diagram", "normal force", "tension"),
                "Draw and solve the free-body diagram for a sign suspended by two cables.",
                (
                    (
                        "diagram diagnostic",
                        "Repair a diagram containing velocity as a force.",
                        (1,),
                    ),
                    ("quantitative", "Solve component force equations from a diagram.", (2,)),
                ),
                (
                    "The normal force always equals weight.",
                    "Velocity belongs on a free-body diagram.",
                ),
                ("A complete, object-centered diagram.", "Equations traceable to diagram arrows."),
            ),
            lesson(
                "m12-friction-inclines",
                "Friction and inclined planes",
                ("m11-free-body-diagrams",),
                (
                    "Distinguish static friction from kinetic friction and determine its direction.",
                    "Predict and calculate the slipping threshold and acceleration on an incline.",
                ),
                ("static friction", "kinetic friction", "inclined plane", "threshold"),
                "Find the minimum incline angle for a block with a stated static-friction coefficient.",
                (
                    (
                        "misconception diagnostic",
                        "Determine whether static friction equals its maximum value.",
                        (1,),
                    ),
                    ("quantitative", "Predict threshold angle and post-slip acceleration.", (1, 2)),
                ),
                (
                    "Static friction always equals mu_s N.",
                    "Friction always opposes velocity rather than impending relative motion.",
                ),
                (
                    "A correct threshold inequality.",
                    "Simulation evidence bracketing the predicted angle.",
                ),
                activity=RoadmapActivity(
                    "inclined_plane",
                    LearningMode.COMPARE,
                    "Bracket the slipping threshold and compare smooth and rough surfaces.",
                    "Prediction, threshold interval, force diagram, and acceleration comparison.",
                ),
                minutes=60,
                extended=True,
            ),
        ),
    ),
    RoadmapUnit(
        "energy",
        "Work and energy",
        (
            lesson(
                "m13-work-kinetic-energy",
                "Work and the kinetic-energy theorem",
                ("m12-friction-inclines",),
                (
                    "Calculate work from force and displacement, including sign and angle.",
                    "Apply the work-kinetic-energy theorem to a defined system.",
                ),
                ("work", "kinetic energy", "power", "system"),
                "Find the stopping distance under a constant friction force using energy.",
                (
                    ("conceptual", "Determine the sign of work by several forces.", (1,)),
                    (
                        "quantitative",
                        "Solve a stopping problem by work-energy and compare with kinematics.",
                        (2,),
                    ),
                ),
                ("Any applied force does positive work.", "Energy is a force consumed by motion."),
                ("A signed work inventory.", "Equivalent energy and kinematics results."),
            ),
            lesson(
                "m14-potential-conservation",
                "Potential energy and conservation",
                ("m13-work-kinetic-energy",),
                (
                    "Define gravitational potential energy for a system and reference level.",
                    "Use energy conservation to predict speed and reachable position.",
                ),
                ("potential energy", "conservation", "reference level", "turning point"),
                "Predict a coaster's speed after descending and its maximum subsequent height.",
                (
                    (
                        "conceptual",
                        "Explain why changing the zero of potential energy cannot change motion.",
                        (1,),
                    ),
                    ("quantitative", "Predict speeds and turning points along a track.", (2,)),
                ),
                (
                    "Potential energy belongs to one object alone.",
                    "Energy conservation means kinetic energy is constant.",
                ),
                (
                    "A consistent system and reference choice.",
                    "Predictions matching ideal simulation metrics.",
                ),
                activity=RoadmapActivity(
                    "roller_coaster",
                    LearningMode.ANALYZE,
                    "Predict speeds and turning points, then inspect kinetic, potential, and total-energy graphs.",
                    "Notebook predictions and graph-based conservation evidence.",
                ),
                minutes=60,
            ),
            lesson(
                "m15-dissipation-energy-review",
                "Dissipation, power, and cumulative energy review",
                ("m14-potential-conservation",),
                (
                    "Track energy transfers when mechanical energy is not conserved.",
                    "Choose force, kinematics, or energy methods and justify the efficient representation.",
                ),
                ("dissipation", "thermal energy", "power", "representation choice"),
                "Determine minimum launch energy for a lossy coaster to finish a track.",
                (
                    ("conceptual", "Locate energy outside the mechanical-energy account.", (1,)),
                    (
                        "cumulative quantitative",
                        "Solve one motion by both force and energy methods.",
                        (1, 2),
                    ),
                ),
                ("Nonconserved mechanical energy has disappeared.",),
                ("A complete energy-account diagram.", "A justified solution-method comparison."),
                activity=RoadmapActivity(
                    "roller_coaster",
                    LearningMode.COMPARE,
                    "Compare ideal and dissipative runs with the same initial state.",
                    "An energy budget that accounts for the change in mechanical energy.",
                ),
                extended=True,
            ),
        ),
    ),
    RoadmapUnit(
        "momentum",
        "Momentum and collisions",
        (
            lesson(
                "m16-impulse-momentum",
                "Impulse and momentum",
                ("m10-interactions-newton", "m13-work-kinetic-energy"),
                (
                    "Relate impulse to momentum change using force-time evidence.",
                    "Choose a system and identify when external impulse is negligible.",
                ),
                ("momentum", "impulse", "system", "external force"),
                "Compute momentum change from a triangular force-time pulse.",
                (
                    ("conceptual", "Choose a system for approximate momentum conservation.", (2,)),
                    ("quantitative", "Calculate impulse as signed graph area.", (1,)),
                ),
                (
                    "Momentum is conserved for each object in a collision.",
                    "Impulse and force have the same units.",
                ),
                ("A justified system boundary.", "A force-time area matching momentum change."),
            ),
            lesson(
                "m17-collision-models",
                "Elastic and inelastic collisions",
                ("m16-impulse-momentum",),
                (
                    "Apply momentum conservation to one-dimensional collisions.",
                    "Use kinetic energy and restitution to distinguish collision models.",
                ),
                ("elastic collision", "inelastic collision", "restitution", "kinetic energy"),
                "Find final velocities for equal-mass elastic and perfectly inelastic collisions.",
                (
                    (
                        "misconception diagnostic",
                        "Distinguish conserved momentum from kinetic energy.",
                        (1, 2),
                    ),
                    ("quantitative", "Predict final velocities and energy change.", (1, 2)),
                ),
                (
                    "Kinetic energy is conserved in every collision.",
                    "Objects that stick must stop.",
                ),
                (
                    "Momentum closure within tolerance.",
                    "Correct classification from energy evidence.",
                ),
                activity=RoadmapActivity(
                    "bumper_cars",
                    LearningMode.COMPARE,
                    "Compare matched elastic, partially inelastic, and sticking collisions.",
                    "Before/after momentum and kinetic-energy tables with model classification.",
                ),
                minutes=60,
                extended=True,
            ),
            lesson(
                "m18-momentum-synthesis",
                "Collision synthesis and cumulative review",
                ("m17-collision-models",),
                (
                    "Solve multistage mechanics problems combining collision and post-collision motion.",
                    "Defend conservation claims using system, interval, and external-interaction evidence.",
                ),
                ("multistage problems", "conservation laws", "model selection"),
                "Analyze a ballistic-pendulum-style collision followed by an energy conversion.",
                (
                    ("conceptual", "Select the valid conservation law for each stage.", (2,)),
                    (
                        "cumulative quantitative",
                        "Solve a collision-plus-motion problem with checks.",
                        (1, 2),
                    ),
                ),
                ("One conservation equation applies unchanged across every stage.",),
                (
                    "A stage diagram with distinct systems and intervals.",
                    "A checked numerical synthesis.",
                ),
                activity=RoadmapActivity(
                    "bumper_cars",
                    LearningMode.ANALYZE,
                    "Use collision graphs to audit a hand-calculated momentum and energy account.",
                    "A discrepancy analysis separating numerical tolerance from model choice.",
                ),
                minutes=60,
                extended=True,
            ),
        ),
    ),
    RoadmapUnit(
        "rotation",
        "Rotation, torque, and center of mass",
        (
            lesson(
                "m19-angular-kinematics",
                "Angular kinematics and rotational inertia",
                ("m05-constant-acceleration", "m14-potential-conservation"),
                (
                    "Connect angular position, velocity, and acceleration to linear analogues.",
                    "Predict how mass distribution changes rotational response and energy.",
                ),
                ("angular kinematics", "moment of inertia", "rotational energy"),
                "Compare angular acceleration and energy for a disk and hoop under equal torque.",
                (
                    (
                        "conceptual",
                        "Rank bodies by rotational response from mass distribution.",
                        (2,),
                    ),
                    ("quantitative", "Calculate angular motion under constant torque.", (1, 2)),
                ),
                (
                    "Moment of inertia depends only on total mass.",
                    "Radians carry an independent physical dimension in formulas.",
                ),
                ("A linear-angular analogy table.", "Predictions matching shape comparisons."),
                activity=RoadmapActivity(
                    "rotational_motion",
                    LearningMode.COMPARE,
                    "Compare disk and hoop responses under matched mass, radius, and torque.",
                    "A moment-of-inertia explanation for angular acceleration and energy differences.",
                ),
                minutes=60,
                extended=True,
            ),
            lesson(
                "m20-torque-equilibrium",
                "Torque, levers, and static equilibrium",
                ("m11-free-body-diagrams", "m19-angular-kinematics"),
                (
                    "Calculate torque using lever arm and force direction.",
                    "Apply translational and rotational equilibrium simultaneously.",
                ),
                ("torque", "lever arm", "static equilibrium", "mechanical advantage"),
                "Find support forces and balance conditions for a loaded beam.",
                (
                    (
                        "misconception diagnostic",
                        "Compare torque from equal forces at different positions and angles.",
                        (1,),
                    ),
                    ("quantitative", "Solve force and torque equilibrium equations.", (1, 2)),
                ),
                (
                    "A larger force always produces a larger torque.",
                    "The pivot force must be omitted from the force balance.",
                ),
                (
                    "A labeled lever-arm diagram.",
                    "Simultaneously satisfied force and torque balances.",
                ),
                activity=RoadmapActivity(
                    "torque_levers",
                    LearningMode.ANALYZE,
                    "Predict balance, vary one lever arm, and compare torque measurements.",
                    "A torque table and a verified equilibrium configuration.",
                ),
                minutes=60,
                extended=True,
            ),
            lesson(
                "m21-center-mass-rotation-review",
                "Center of mass and rotational synthesis",
                ("m20-torque-equilibrium",),
                (
                    "Calculate center of mass as a mass-weighted position and interpret its frame dependence.",
                    "Use center of mass, force, torque, and energy in a cumulative rigid-system analysis.",
                ),
                ("center of mass", "balance", "weighted average", "rigid systems"),
                "Locate the center of mass of three point masses and predict a balancing pivot.",
                (
                    ("conceptual", "Predict how moving one mass shifts the center of mass.", (1,)),
                    (
                        "cumulative quantitative",
                        "Solve a balance problem using center of mass and torque.",
                        (1, 2),
                    ),
                ),
                (
                    "The center of mass must lie inside an object.",
                    "Center of mass and geometric center are always identical.",
                ),
                (
                    "A verified weighted-average calculation.",
                    "A balance prediction confirmed by torque evidence.",
                ),
                activity=RoadmapActivity(
                    "center_of_mass",
                    LearningMode.COMPARE,
                    "Compare equal and unequal mass arrangements and predict the balance point.",
                    "Predictions and measured center-of-mass shifts for at least three arrangements.",
                ),
                minutes=60,
            ),
        ),
    ),
    RoadmapUnit(
        "gravitation",
        "Gravitation, orbital motion, and course synthesis",
        (
            lesson(
                "m22-universal-gravitation",
                "Universal gravitation and gravitational energy",
                ("m14-potential-conservation", "m02-vectors-coordinates"),
                (
                    "Apply the inverse-square gravitational force law with correct vector direction.",
                    "Relate gravitational force, field, potential energy, and escape energy.",
                ),
                (
                    "universal gravitation",
                    "inverse square",
                    "field",
                    "gravitational potential energy",
                ),
                "Calculate surface gravity and escape speed for a spherical planet.",
                (
                    (
                        "conceptual",
                        "Predict inverse-square changes without confusing field and potential.",
                        (1, 2),
                    ),
                    (
                        "quantitative",
                        "Compute force, energy, and escape speed with limiting checks.",
                        (1, 2),
                    ),
                ),
                (
                    "Astronauts in orbit experience no gravity.",
                    "Gravitational potential energy is mgh at every distance.",
                ),
                (
                    "Correct inverse-square ratios.",
                    "A dimensionally and physically checked escape calculation.",
                ),
                extended=True,
            ),
            lesson(
                "m23-orbits",
                "Circular, elliptical, and escape trajectories",
                ("m22-universal-gravitation", "m08-projectile-components"),
                (
                    "Explain orbit as continuous free fall and calculate circular-orbit conditions.",
                    "Use energy and angular-momentum evidence to distinguish bound, impact, and escape trajectories.",
                ),
                ("orbit", "centripetal acceleration", "escape", "numerical integration"),
                "Calculate circular orbital speed and period at a specified radius.",
                (
                    (
                        "misconception diagnostic",
                        "Explain why a spacecraft needs no forward thrust in an ideal orbit.",
                        (1,),
                    ),
                    (
                        "quantitative",
                        "Predict trajectory class from launch speed and energy.",
                        (1, 2),
                    ),
                ),
                (
                    "A centripetal force is an extra force in addition to gravity.",
                    "Orbiting requires continuous engine thrust.",
                ),
                (
                    "A correct circular-speed prediction.",
                    "Trajectory classification supported by energy and simulation evidence.",
                ),
                activity=RoadmapActivity(
                    "orbital_gravity",
                    LearningMode.COMPARE,
                    "Compare impact, bound elliptical, near-circular, and escape launches.",
                    "A trajectory taxonomy with energy and speed evidence.",
                ),
                minutes=65,
                extended=True,
            ),
            lesson(
                "m24-mechanics-synthesis",
                "Introductory Mechanics cumulative synthesis",
                ("m18-momentum-synthesis", "m21-center-mass-rotation-review", "m23-orbits"),
                (
                    "Select and connect kinematic, force, momentum, energy, and rotational representations.",
                    "Construct, test, and critique a mechanics model using assumptions, units, evidence, and limits.",
                ),
                ("model selection", "conservation", "evidence", "limitations"),
                "Solve a staged launch-and-collision scenario using at least three mechanics frameworks.",
                (
                    (
                        "cumulative conceptual",
                        "Defend a representation and conservation-law choice for each stage.",
                        (1,),
                    ),
                    (
                        "cumulative quantitative",
                        "Complete a multirepresentation problem with validation and error analysis.",
                        (1, 2),
                    ),
                ),
                (
                    "The most advanced equation is always the best method.",
                    "Agreement with one result proves every assumption.",
                ),
                (
                    "A coherent solution map across at least three units.",
                    "A final claim-evidence-assumptions-limitations defense.",
                ),
                activity=RoadmapActivity(
                    "cannonball",
                    LearningMode.MODEL,
                    "Audit an earlier projectile notebook run, its assumptions, analytic prediction, and numerical evidence.",
                    "A revised model claim connected to course-wide force and energy reasoning.",
                ),
                minutes=75,
                extended=True,
            ),
        ),
    ),
)


INTRODUCTORY_MECHANICS_LESSONS = tuple(
    lesson_item for unit in INTRODUCTORY_MECHANICS_UNITS for lesson_item in unit.lessons
)


def validate_mechanics_roadmap(*, simulation_ids: set[str]) -> None:
    """Validate IDs, ordered prerequisites, objective references, and simulations."""

    unit_ids = [unit.id for unit in INTRODUCTORY_MECHANICS_UNITS]
    lesson_ids = [item.id for item in INTRODUCTORY_MECHANICS_LESSONS]
    if len(unit_ids) != len(set(unit_ids)) or len(lesson_ids) != len(set(lesson_ids)):
        raise PhysicsValidationError("Roadmap unit and lesson IDs must be unique.")
    position = {lesson_id: index for index, lesson_id in enumerate(lesson_ids)}
    for item in INTRODUCTORY_MECHANICS_LESSONS:
        if item.estimated_minutes <= 0 or not item.mathematical_depths:
            raise PhysicsValidationError(f"Invalid duration or depth for {item.id}.")
        if len(item.objectives) < 2 or not item.worked_examples or not item.assessments:
            raise PhysicsValidationError(f"Incomplete instructional specification for {item.id}.")
        objective_ids = {objective_item.id for objective_item in item.objectives}
        if len(objective_ids) != len(item.objectives):
            raise PhysicsValidationError(f"Duplicate objective IDs in {item.id}.")
        for prerequisite in item.prerequisite_lesson_ids:
            if prerequisite not in position or position[prerequisite] >= position[item.id]:
                raise PhysicsValidationError(f"Invalid or cyclic prerequisite {prerequisite!r}.")
        for assessment in item.assessments:
            if not assessment.objective_ids or not set(assessment.objective_ids) <= objective_ids:
                raise PhysicsValidationError(f"Unknown objective reference in {item.id}.")
        for activity in item.simulation_activities:
            if activity.simulation_id not in simulation_ids:
                raise PhysicsValidationError(
                    f"Unknown simulation {activity.simulation_id!r} in {item.id}."
                )
