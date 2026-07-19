"""Complete example lesson built around the Cannonball Launcher simulation."""

from physics_playground.education.assessments import AssessmentDefinition
from physics_playground.education.audience import MathematicalDepth
from physics_playground.education.models import (
    ActivityPhase,
    AnswerChoice,
    CheckpointQuestion,
    Concept,
    ContentDepth,
    ContentProfile,
    ContentVoice,
    DerivationStep,
    DiagramSpec,
    GuidedDerivation,
    KnownValue,
    LearningObjective,
    Lesson,
    LessonSection,
    MisconceptionCallout,
    Prerequisite,
    PrerequisiteKind,
    Quantity,
    QuestionKind,
    ReasoningStep,
    SimulationActivity,
    Subject,
    Substitution,
    Unit,
    WorkedExample,
)
from physics_playground.models.simulations import LearningMode
from physics_playground.subjects.mechanics.foundations_lesson import (
    FOUNDATION_CONCEPTS,
    MODELS_MEASUREMENTS_LESSON,
)
from physics_playground.subjects.mechanics.kinematics_lessons import (
    KINEMATICS_CONCEPTS,
    KINEMATICS_LESSONS,
    VECTORS_LESSON,
)

PROJECTILE_CONCEPTS = (
    Concept(
        "vectors",
        "Vector components",
        "A vector can be resolved into perpendicular components that evolve independently.",
        ("v_x", "v_y"),
        ("kinematics",),
    ),
    Concept(
        "kinematics",
        "Constant-acceleration kinematics",
        "Position and velocity relations for motion under constant acceleration.",
        ("x", "y", "v", "a", "t"),
        ("vectors", "projectile_motion"),
    ),
    Concept(
        "projectile_motion",
        "Projectile motion",
        "Two-dimensional motion with horizontal and vertical components linked by time.",
        ("R", "v_0", "theta", "g"),
        ("vectors", "kinematics"),
    ),
)

OBJECTIVES = (
    LearningObjective(
        "projectile-components",
        "Resolve an initial velocity into horizontal and vertical components.",
        "Correctly calculate v_x and v_y with units for a chosen launch.",
    ),
    LearningObjective(
        "projectile-range",
        "Derive and apply the level-ground projectile range relation.",
        "Explain each symbolic step and verify the final dimensions are length.",
    ),
    LearningObjective(
        "projectile-model-limits",
        "Evaluate when the ideal projectile model is useful and when it fails.",
        "Compare ideal and drag runs and identify at least two model limitations.",
    ),
)

ACTIVITIES = (
    SimulationActivity(
        "predict-angle",
        ActivityPhase.PREDICTION,
        "cannonball",
        "Predict the best angle",
        (
            "Keep launch speed fixed at 20 m/s and drag off.",
            "Predict which of 30°, 45°, and 60° travels farthest before running the model.",
            "Record a physical reason for the prediction.",
        ),
        LearningMode.EXPLORE,
        "Which component tradeoff controls the range?",
        "A recorded angle prediction and explanation.",
        objective_ids=("projectile-range",),
    ),
    SimulationActivity(
        "explore-components",
        ActivityPhase.EXPLORATION,
        "cannonball",
        "Explore component changes",
        (
            "Run 30°, 45°, and 60° launches at the same speed.",
            "Observe time aloft, maximum height, and range.",
            "Relate each outcome to v_x and v_y.",
        ),
        LearningMode.EXPLORE,
        "What changes, and what stays symmetric around 45°?",
        "Three completed runs with component-based observations.",
        objective_ids=("projectile-components",),
    ),
    SimulationActivity(
        "compare-complements",
        ActivityPhase.COMPARISON,
        "cannonball",
        "Compare complementary angles",
        (
            "Compare 30° and 60° with identical speed and no drag.",
            "Overlay the trajectories.",
            "Explain their equal ideal ranges and different peak heights.",
        ),
        LearningMode.COMPARE,
        "Why can two visibly different paths land at the same range?",
        "A comparison citing both horizontal speed and flight time.",
        objective_ids=("projectile-components", "projectile-range"),
    ),
    SimulationActivity(
        "analyze-range",
        ActivityPhase.ANALYSIS,
        "cannonball",
        "Analyze range versus angle",
        (
            "Sweep launch angle while speed remains fixed.",
            "Locate the ideal-model maximum on the range graph.",
            "Check the symmetry of complementary angles.",
        ),
        LearningMode.ANALYZE,
        "How does the graph encode sin(2 theta)?",
        "A graph-based estimate of the maximizing angle.",
        objective_ids=("projectile-range",),
    ),
    SimulationActivity(
        "model-drag",
        ActivityPhase.MODELING,
        "cannonball",
        "Challenge the ideal model",
        (
            "Build matched ideal and quadratic-drag runs.",
            "Compare range, peak height, and path symmetry.",
            "State which assumptions changed and which equations no longer apply directly.",
        ),
        LearningMode.MODEL,
        "Which ideal conclusions survive when drag is included?",
        "A model comparison naming assumptions and evidence.",
        objective_ids=("projectile-model-limits",),
    ),
    SimulationActivity(
        "reflect-model",
        ActivityPhase.REFLECTION,
        "cannonball",
        "Reflect on evidence and limits",
        (
            "Return to the original prediction.",
            "Explain whether the evidence supported it.",
            "Name one real launch where the point-mass, flat-ground model would be inadequate.",
        ),
        None,
        "What did the living figure reveal that the equation alone did not?",
        "A claim-evidence-limitation reflection.",
        objective_ids=("projectile-model-limits",),
    ),
)

RANGE_DERIVATION = GuidedDerivation(
    "derive-range",
    "Derive the level-ground range",
    "Eliminate time to express horizontal range in terms of launch speed, angle, and gravity.",
    (
        "The projectile is a point mass.",
        "Gravity is uniform and downward.",
        "Air resistance is neglected.",
        "Launch and landing heights are equal.",
    ),
    (
        DerivationStep(
            "resolve-velocity",
            1,
            "Resolve the launch velocity.",
            "v_x = v_0 cos(theta),  v_y = v_0 sin(theta)",
            "The chosen x-axis is horizontal and y-axis is upward.",
            "Draw the right triangle formed by v_0 and its components.",
        ),
        DerivationStep(
            "vertical-position",
            2,
            "Write vertical position relative to launch height.",
            "y(t) = v_0 sin(theta)t - (1/2)gt^2",
            "Only gravity accelerates the ideal projectile vertically.",
        ),
        DerivationStep(
            "flight-time",
            3,
            "Set y=0 at landing and select the nonzero root.",
            "t_f = 2v_0 sin(theta)/g",
            "The zero root is launch; the second root is landing.",
        ),
        DerivationStep(
            "horizontal-range",
            4,
            "Insert flight time into horizontal position.",
            "R = v_0 cos(theta)t_f = v_0^2 sin(2theta)/g",
            "The identity 2sin(theta)cos(theta)=sin(2theta) exposes angle symmetry.",
        ),
    ),
    "For this idealized geometry, R=v_0^2 sin(2theta)/g and complementary angles have equal range.",
    frozenset({MathematicalDepth.STANDARD, MathematicalDepth.EXTENDED}),
)

RANGE_EXAMPLE = WorkedExample(
    "range-example",
    "Range of a 20 m/s launch",
    "Find the ideal range of a projectile launched at 45° from and onto level ground.",
    (
        KnownValue(Quantity("v_0", "initial speed", "m/s"), 20.0),
        KnownValue(Quantity("theta", "launch angle", "deg"), 45.0),
        KnownValue(Quantity("g", "gravitational acceleration", "m/s^2"), 9.81),
    ),
    Quantity("R", "horizontal range", "m"),
    (
        ReasoningStep(
            "choose-model",
            "R = v_0^2 sin(2theta)/g",
            "Equal launch and landing heights allow the derived range relation.",
        ),
        ReasoningStep(
            "maximize-angle",
            "sin(2 x 45°) = sin(90°) = 1",
            "The chosen angle maximizes ideal range for fixed speed.",
        ),
    ),
    (
        Substitution("R = (20.0 m/s)^2 sin(90°)/(9.81 m/s^2)", "R = 400/9.81 m"),
        Substitution("R = 40.77 m", "R approximately 40.8 m"),
    ),
    "(m/s)^2 divided by (m/s^2) = m, so the result has dimensions of length.",
    "R approximately 40.8 m",
    "The ideal projectile lands about 40.8 m away; drag would shorten this range.",
)

CANNONBALL_LESSON = Lesson(
    "projectile-motion-from-components",
    "Projectile motion from components",
    "Connect a living trajectory to vector components, kinematics, evidence, and model limits.",
    OBJECTIVES,
    (
        Prerequisite(
            "constant-acceleration-prerequisite",
            PrerequisiteKind.LESSON,
            "m05-constant-acceleration",
            "Constant-acceleration graph reasoning supports the two component equations.",
        ),
        Prerequisite(
            "trigonometry-prerequisite",
            PrerequisiteKind.LESSON,
            VECTORS_LESSON.id,
            "Resolving the launch velocity uses sine and cosine in a right triangle; Vectors and components teaches that decomposition before it is required here.",
        ),
        Prerequisite(
            "algebra-prerequisite",
            PrerequisiteKind.SKILL,
            "solve-quadratic-roots",
            "The range derivation selects a nonzero root of the vertical equation.",
        ),
    ),
    ("vectors", "kinematics", "projectile_motion"),
    ("cannonball",),
    (
        LessonSection(
            "system-and-prediction",
            "The physical system and a prediction",
            "A projectile leaves a launcher with initial speed v_0 at angle theta. We choose +x horizontal and +y upward, then predict before revealing the trajectory.",
            (
                DiagramSpec(
                    "projectile-components-figure",
                    "projectile-components",
                    "Launch velocity components and coordinate choices",
                    (
                        "A projectile launches up and to the right. The initial velocity arrow "
                        "is resolved into a rightward component v_x and upward component v_y. "
                        "The x-axis points right, the y-axis points up, and gravity points down."
                    ),
                    ("projectile-components",),
                ),
                ACTIVITIES[0],
                CheckpointQuestion(
                    "component-checkpoint",
                    "A projectile is launched at 20.0 m/s and 60°. What is its initial horizontal velocity component?",
                    QuestionKind.NUMERIC,
                    ("projectile-components",),
                    unit_options=("m/s", "km/h"),
                ),
            ),
        ),
        LessonSection(
            "laws-and-derivation",
            "Coordinate choices, laws, and derivation",
            "Newton's second law gives zero horizontal acceleration and vertical acceleration -g under the ideal assumptions. The components share time but otherwise evolve independently.",
            (RANGE_DERIVATION, ACTIVITIES[1], ACTIVITIES[2]),
            ContentProfile(ContentDepth.ADVANCED, ContentVoice.ACADEMIC),
        ),
        LessonSection(
            "worked-example",
            "Worked example with units",
            "Apply the symbolic result only after checking that its assumptions match the system.",
            (
                RANGE_EXAMPLE,
                CheckpointQuestion(
                    "range-checkpoint",
                    "With speed fixed and drag absent, which angle has the same range as 30°?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("projectile-range",),
                    (
                        AnswerChoice("angle-45", "45°"),
                        AnswerChoice("angle-60", "60°"),
                        AnswerChoice("angle-75", "75°"),
                    ),
                ),
                ACTIVITIES[3],
            ),
        ),
        LessonSection(
            "validation-and-limits",
            "Validation, limiting cases, and model limitations",
            "Check theta=0° and 90°: the level-ground range tends to zero. Check dimensions and compare simulation output with the analytic result. Then add drag to expose the limits of uniform gravity, flat ground, point-mass motion, and a still atmosphere.",
            (
                MisconceptionCallout(
                    "horizontal-force-misconception",
                    "A forward force must keep pushing the projectile after launch.",
                    "In the ideal model, horizontal velocity persists without a horizontal net force; gravity changes only v_y.",
                    "What does the horizontal velocity graph do after launch?",
                ),
                MisconceptionCallout(
                    "universal-45-degree-misconception",
                    "A 45° launch always gives maximum range.",
                    "The 45° result requires equal launch and landing heights, negligible drag, uniform gravity, and fixed launch speed. Change those conditions and the maximizing angle can change.",
                    "Which assumption fails for a launch from a cliff or through substantial air drag?",
                ),
                ACTIVITIES[4],
                CheckpointQuestion(
                    "model-limit-checkpoint",
                    "Which change invalidates direct use of R=v_0² sin(2theta)/g?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("projectile-model-limits",),
                    (
                        AnswerChoice("add-drag", "Include substantial air resistance."),
                        AnswerChoice(
                            "rename-axis", "Rename the horizontal axis while keeping its direction."
                        ),
                        AnswerChoice(
                            "more-samples", "Display more samples from the same ideal model."
                        ),
                    ),
                ),
                ACTIVITIES[5],
            ),
        ),
        LessonSection(
            "numerical-extension",
            "Advanced extension: from equations to numerical trajectories",
            "With quadratic drag, acceleration depends on velocity, so the ideal closed-form range relation no longer describes the full path. The simulation advances the coupled state in small time steps, checks landing as an event, and exposes time-step and maximum-time limits. Compare smaller time steps to test numerical convergence before interpreting a difference as physical.",
            (),
            ContentProfile(ContentDepth.ADVANCED, ContentVoice.ACADEMIC),
            frozenset({MathematicalDepth.EXTENDED}),
        ),
    ),
    ACTIVITIES,
    ContentProfile(ContentDepth.STANDARD, ContentVoice.APPROACHABLE),
    55,
    None,
    "Forces on an inclined plane",
)

CANNONBALL_ASSESSMENTS = (
    AssessmentDefinition(
        id="range-checkpoint",
        lesson_id=CANNONBALL_LESSON.id,
        kind=QuestionKind.MULTIPLE_CHOICE,
        objective_ids=("projectile-range",),
        success_feedback=(
            "Complementary angles have equal sin(2theta), so 30° and 60° share a range."
        ),
        retry_feedback="Revisit the complementary-angle comparison, then try again.",
        correct_choice_ids=("angle-60",),
        hints=("Compare the value of 2theta for each candidate angle.",),
        remediation_lesson_ids=(),
        misconception_by_choice=(
            ("angle-45", "maximum-range-confused-with-complement"),
            ("angle-75", "angles-must-sum-to-90"),
        ),
    ),
    AssessmentDefinition(
        id="component-checkpoint",
        lesson_id=CANNONBALL_LESSON.id,
        kind=QuestionKind.NUMERIC,
        objective_ids=("projectile-components",),
        success_feedback="Correct: v_x=v_0 cos(theta)=20.0 cos(60°)=10.0 m/s.",
        retry_feedback="Resolve the velocity arrow along the horizontal axis using cosine.",
        expected_numeric_value=10.0,
        canonical_unit="m/s",
        absolute_tolerance=0.1,
        hints=("Use the side adjacent to the launch angle: v_x=v_0 cos(theta).",),
    ),
    AssessmentDefinition(
        id="model-limit-checkpoint",
        lesson_id=CANNONBALL_LESSON.id,
        kind=QuestionKind.MULTIPLE_CHOICE,
        objective_ids=("projectile-model-limits",),
        success_feedback="Correct: substantial drag changes the acceleration and breaks the ideal range derivation.",
        retry_feedback="Ask which option changes a physical assumption used in the derivation.",
        correct_choice_ids=("add-drag",),
        hints=("Changing display detail is not the same as changing the physical model.",),
        misconception_by_choice=(
            ("rename-axis", "notation-changes-physics"),
            ("more-samples", "display-resolution-changes-model"),
        ),
    ),
)

MECHANICS_SUBJECT = Subject(
    "mechanics",
    "Mechanics",
    "Use forces, motion, energy, and momentum to explain how physical systems change.",
    (*FOUNDATION_CONCEPTS, *KINEMATICS_CONCEPTS, *PROJECTILE_CONCEPTS),
    (
        Unit(
            "mechanics-foundations",
            "Measurement, models, vectors, and graphs",
            "Establish the evidence and representation habits used throughout mechanics.",
            tuple(objective.id for objective in MODELS_MEASUREMENTS_LESSON.objectives),
            (MODELS_MEASUREMENTS_LESSON,),
        ),
        Unit(
            "introductory-kinematics",
            "Introductory kinematics",
            "Connect coordinates, motion graphs, acceleration, and two-dimensional motion.",
            tuple(objective.id for lesson in KINEMATICS_LESSONS for objective in lesson.objectives),
            KINEMATICS_LESSONS,
        ),
        Unit(
            "motion-in-two-dimensions",
            "Motion in two dimensions",
            "Connect vector components to trajectories and evidence.",
            tuple(objective.id for objective in OBJECTIVES),
            (CANNONBALL_LESSON,),
        ),
    ),
)
