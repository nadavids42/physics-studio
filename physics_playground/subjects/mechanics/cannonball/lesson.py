"""Complete example lesson built around the Cannonball Launcher simulation."""

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
        {"initial_speed_m_s": 20.0, "launch_angle_deg": 45.0, "drag_enabled": False},
        "Which component tradeoff controls the range?",
        "A recorded angle prediction and explanation.",
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
        {"initial_speed_m_s": 20.0, "drag_enabled": False},
        "What changes, and what stays symmetric around 45°?",
        "Three completed runs with component-based observations.",
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
        {"initial_speed_m_s": 20.0, "drag_enabled": False},
        "Why can two visibly different paths land at the same range?",
        "A comparison citing both horizontal speed and flight time.",
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
        {"initial_speed_m_s": 20.0, "drag_enabled": False},
        "How does the graph encode sin(2 theta)?",
        "A graph-based estimate of the maximizing angle.",
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
        {"initial_speed_m_s": 20.0, "launch_angle_deg": 45.0},
        "Which ideal conclusions survive when drag is included?",
        "A model comparison naming assumptions and evidence.",
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
        {},
        "What did the living figure reveal that the equation alone did not?",
        "A claim-evidence-limitation reflection.",
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
            "vectors-prerequisite",
            PrerequisiteKind.CONCEPT,
            "vectors",
            "Learners need basic vector-component reasoning.",
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
            (ACTIVITIES[0],),
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
                    "angle-60",
                    "Complementary angles have equal sin(2theta), so 30° and 60° share a range.",
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
                ACTIVITIES[4],
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

MECHANICS_SUBJECT = Subject(
    "mechanics",
    "Mechanics",
    "Use forces, motion, energy, and momentum to explain how physical systems change.",
    PROJECTILE_CONCEPTS,
    (
        Unit(
            "motion-in-two-dimensions",
            "Motion in two dimensions",
            "Connect vector components to trajectories and evidence.",
            tuple(objective.id for objective in OBJECTIVES),
            (CANNONBALL_LESSON,),
        ),
    ),
)
