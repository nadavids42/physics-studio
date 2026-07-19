"""Lesson 1: Models, Measurements, and Representations."""

from physics_playground.education.assessments import AssessmentDefinition
from physics_playground.education.models import (
    ActivityPhase,
    AnswerChoice,
    CheckpointQuestion,
    Concept,
    DiagramSpec,
    KnownValue,
    LearningObjective,
    Lesson,
    LessonSection,
    MisconceptionCallout,
    Quantity,
    QuestionKind,
    ReasoningStep,
    SimulationActivity,
    Substitution,
    WorkedExample,
)
from physics_playground.models.simulations import LearningMode

FOUNDATION_CONCEPTS = (
    Concept(
        "physical_models",
        "Physical systems and models",
        "A physical system is the part of reality under study; a model is a purposeful representation that keeps selected features and assumptions.",
        related_concept_ids=("measurement", "representations"),
    ),
    Concept(
        "measurement",
        "Measurement and uncertainty",
        "A measurement is a quantity compared with a unit and reported with justified precision and uncertainty.",
        related_concept_ids=("physical_models", "representations"),
    ),
    Concept(
        "representations",
        "Scientific representations",
        "Graphs, diagrams, tables, equations, and simulations emphasize different relationships in a system or model.",
        related_concept_ids=("physical_models", "measurement"),
    ),
)

OBJECTIVES = (
    LearningObjective(
        "m01-model-critique",
        "Distinguish a physical system from a model and identify assumptions and limitations.",
        "A correct system–model–assumption–limitation analysis and checkpoint response.",
    ),
    LearningObjective(
        "m01-measurement",
        "Report quantities with units, justified precision, and introductory uncertainty.",
        "A worked measurement with coherent units and a precision claim supported by the instrument resolution.",
    ),
    LearningObjective(
        "m01-representations",
        "Identify independent and dependent variables and read evidence from graphs and diagrams.",
        "A graph reading and a comparison of scaled and schematic representations.",
    ),
    LearningObjective(
        "m01-inquiry",
        "Use prediction, observation, and reflection to distinguish scientific reasoning from control manipulation.",
        "A claim supported by a recorded observation, with uncertainty and a stated simulation limitation.",
    ),
)

ACTIVITIES = (
    SimulationActivity(
        "m01-predict-representation",
        ActivityPhase.PREDICTION,
        "cannonball",
        "Predict what a representation can tell you",
        (
            "Before running anything, predict whether a trajectory picture or a range-versus-angle graph better supports an exact range comparison.",
            "Give a reason based on what each representation encodes—not on which looks more realistic. Do not run the simulation until the prediction is recorded.",
        ),
        LearningMode.EXPLORE,
        {"initial_speed_m_s": 20.0, "launch_angle_deg": 45.0, "drag_enabled": False},
        "Which representation would you choose, and what evidence could it supply?",
        "A prediction that identifies the representation and the evidence expected from it.",
        objective_ids=("m01-representations", "m01-inquiry"),
    ),
    SimulationActivity(
        "m01-guided-observation",
        ActivityPhase.EXPLORATION,
        "cannonball",
        "Guided observation: change one variable",
        (
            "Open Explore mode and keep speed at 20 m/s, drag off, and the world on Earth.",
            "Run 30° and 45° launches. Treat launch angle as the independent variable and range as the dependent variable.",
            "Record both ranges with units and one limitation on their precision.",
            "Do not merely report that you moved a control: state what changed, what was held fixed, and what the result shows.",
        ),
        LearningMode.EXPLORE,
        {"initial_speed_m_s": 20.0, "drag_enabled": False},
        "What was changed, what was controlled, what was measured, and what uncertainty or display limit applies?",
        "A controlled comparison containing two measured ranges, units, and a limitation.",
        objective_ids=("m01-measurement", "m01-inquiry"),
        evidence_prompt="Record your controlled observation and reasoning",
    ),
    SimulationActivity(
        "m01-read-graph",
        ActivityPhase.ANALYSIS,
        "cannonball",
        "Read the range graph",
        (
            "Open Analyze mode and locate 45° on the horizontal axis.",
            "Read the corresponding ideal range from the vertical axis; include units and avoid claiming more precision than the graph supports.",
            "Name the independent and dependent variables and describe the trend on either side of 45°.",
        ),
        LearningMode.ANALYZE,
        {"initial_speed_m_s": 20.0, "drag_enabled": False},
        "What does one point mean, and what relationship does the full curve show?",
        "A coordinate reading plus a trend statement tied to the graph axes.",
        objective_ids=("m01-measurement", "m01-representations"),
        evidence_prompt="Record the graph coordinate, axis variables, and trend",
    ),
    SimulationActivity(
        "m01-reflect-inquiry",
        ActivityPhase.REFLECTION,
        "cannonball",
        "Reflect on simulation evidence",
        (
            "Return to your prediction and compare it with the observations.",
            "Explain why changing controls alone is not scientific reasoning.",
            "State one way this simulation differs from an experiment and one model limitation.",
        ),
        None,
        {},
        "What turns a simulation run into evidence for a claim?",
        "A claim–evidence–reasoning reflection with a limitation and an experiment comparison.",
        objective_ids=("m01-model-critique", "m01-inquiry"),
    ),
)

MEASUREMENT_EXAMPLE = WorkedExample(
    "m01-walking-speed-example",
    "Estimate a walking speed",
    "A tape marked every 0.1 m gives a distance of 6.0 m. A stopwatch marked every 0.1 s gives a time of 4.1 s. Estimate the average speed and report sensible precision.",
    (
        KnownValue(Quantity("d", "distance", "m"), 6.0, "6.0 ± 0.1 m"),
        KnownValue(Quantity("t", "elapsed time", "s"), 4.1, "4.1 ± 0.1 s"),
    ),
    Quantity("v_avg", "average speed", "m/s"),
    (
        ReasoningStep(
            "define-speed",
            "v_avg = d/t",
            "Distance is the dependent measurement accumulated during the timed interval.",
        ),
        ReasoningStep(
            "estimate-resolution",
            "delta v/v ≈ delta d/d + delta t/t",
            "An introductory worst-case estimate combines the fractional measurement limits.",
        ),
    ),
    (
        Substitution("v_avg = (6.0 m)/(4.1 s)", "v_avg = 1.463... m/s"),
        Substitution("delta v/v ≈ 0.1/6.0 + 0.1/4.1 ≈ 0.041", "delta v ≈ 0.06 m/s"),
    ),
    "metres divided by seconds gives m/s; the uncertainty has the same unit as speed.",
    "v_avg ≈ (1.46 ± 0.06) m/s",
    "Reporting 1.4634146 m/s would add digits the measurements cannot justify. The estimate may be precise but still inaccurate if reaction time creates a systematic bias.",
)

MODELS_MEASUREMENTS_LESSON = Lesson(
    "m01-measurement-models",
    "Models, Measurements, and Representations",
    "Learn the evidence habits used throughout Physics Studio: define a system, choose a model and representation, measure with units and uncertainty, and reason from controlled observations.",
    OBJECTIVES,
    (),
    ("physical_models", "measurement", "representations"),
    ("cannonball",),
    (
        LessonSection(
            "systems-and-models",
            "Physical systems and useful models",
            "The physical system is what we choose to study: for example, a launcher, projectile, Earth, and surrounding air. A model is not a small copy of that system. It is a purposeful set of quantities, relationships, assumptions, and limits. The ideal Cannonball model treats the projectile as a point, uses uniform downward gravity, and can omit air resistance. Those choices make patterns visible, but they also limit which real launches the model can describe. A simulation executes a model; it is not the physical system and it is not automatically an experiment.",
            (
                MisconceptionCallout(
                    "m01-model-copy",
                    "A model is a complete miniature copy of reality.",
                    "Every model selects features for a purpose. Its omissions and assumptions determine where its conclusions apply.",
                    "Which parts of a spinning, irregular ball are absent from a point-particle model?",
                ),
                CheckpointQuestion(
                    "m01-model-check",
                    "Which statement correctly distinguishes the system from the model?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("m01-model-critique",),
                    (
                        AnswerChoice(
                            "system-reality",
                            "The system is the selected part of reality; the model is a purposeful representation with assumptions.",
                        ),
                        AnswerChoice(
                            "model-perfect",
                            "The model is the exact system represented with more decimal places.",
                        ),
                        AnswerChoice(
                            "simulation-experiment",
                            "The simulation is the physical experiment because both display measurements.",
                        ),
                    ),
                ),
            ),
        ),
        LessonSection(
            "quantities-and-measurement",
            "Quantities, units, uncertainty, precision, and accuracy",
            "A physical quantity needs a value and a unit. Measurement resolution and repeatability limit precision; accuracy describes closeness to an accepted or true value. Extra displayed digits do not create information. At this level, report an honest uncertainty based on instrument resolution or variation across repeated measurements, and keep calculated digits consistent with that uncertainty.",
            (
                MEASUREMENT_EXAMPLE,
                MisconceptionCallout(
                    "m01-decimals-accuracy",
                    "More decimal places always mean greater accuracy.",
                    "Digits can increase reported precision without reducing calibration error, reaction-time bias, or model error.",
                    "Can five stopwatch digits correct a clock that runs slow?",
                ),
                CheckpointQuestion(
                    "m01-precision-check",
                    "A ruler is marked every 0.1 cm. Which report best matches its resolution for a length near twelve centimetres?",
                    QuestionKind.MULTIPLE_CHOICE,
                    ("m01-measurement",),
                    (
                        AnswerChoice("honest", "12.3 ± 0.1 cm"),
                        AnswerChoice("false-precision", "12.300000 cm exactly"),
                        AnswerChoice("no-unit", "12.3"),
                    ),
                ),
                ACTIVITIES[0],
            ),
        ),
        LessonSection(
            "diagrams-and-observation",
            "Diagrams and controlled observations",
            "A schematic diagram emphasizes relationships and may not be to scale. A scaled visual preserves selected spatial ratios. Neither is automatically superior: a force arrow may be enlarged for legibility, while a trajectory plot may use meaningful axis scales. Always read labels and captions. In an investigation, choose an independent variable to change, a dependent variable to observe, and controls to hold fixed. Changing controls without a prediction, controlled comparison, recorded observation, and reasoning is exploration—not yet scientific reasoning.",
            (
                DiagramSpec(
                    "m01-representation-figure",
                    "projectile-components",
                    "A schematic projectile diagram with coordinate axes and velocity components",
                    "A projectile is shown moving up and right. Coordinate axes, a downward gravity arrow, and horizontal and vertical velocity-component arrows are enlarged and labeled. The arrows communicate direction and decomposition; their drawn lengths should not be assumed to match the scene scale unless a scale is stated.",
                    ("m01-representations",),
                ),
                ACTIVITIES[1],
            ),
        ),
        LessonSection(
            "graphs-as-evidence",
            "Graphs as representations",
            "A graph maps variables: the independent variable is conventionally placed on the horizontal axis and the dependent variable on the vertical axis. One point describes a paired measurement; the pattern across points describes a relationship. Check axis labels, units, scale, and sampling before interpreting shape. A smooth simulation curve may show model output at many inputs, while experimental points usually include scatter and measurement uncertainty.",
            (
                ACTIVITIES[2],
                CheckpointQuestion(
                    "m01-graph-check",
                    "For the ideal 20 m/s launch, read the range at 45° from the analysis graph. Report a value appropriate to the graph's precision.",
                    QuestionKind.NUMERIC,
                    ("m01-measurement", "m01-representations"),
                    unit_options=("m", "cm"),
                ),
                MisconceptionCallout(
                    "m01-graph-picture",
                    "A graph is a literal picture of the object's path.",
                    "A graph represents a relationship between its axis variables. A range-versus-angle graph is not the projectile's trajectory through space.",
                    "What quantity does each axis encode?",
                ),
            ),
        ),
        LessonSection(
            "simulation-experiment-reflection",
            "Simulation, experiment, and scientific reasoning",
            "A simulation gives reproducible output for its code, parameters, numerical method, and model assumptions, within numerical precision; that does not make its prediction exact for nature. An experiment interacts with a physical system and includes instrument limits, uncontrolled variation, and possible bias. Both require questions, controlled comparisons, evidence, and critique. Running a simulation or opening a lesson records no mastery by itself.",
            (ACTIVITIES[3],),
        ),
    ),
    ACTIVITIES,
    estimated_minutes=50,
    next_lesson_id="m02-position-velocity",
    next_lesson_title="Position, displacement, velocity, and speed",
)

MODELS_MEASUREMENTS_ASSESSMENTS = (
    AssessmentDefinition(
        "m01-model-check",
        MODELS_MEASUREMENTS_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("m01-model-critique",),
        "Correct: models are selective representations whose assumptions define their reach.",
        "Separate the chosen part of reality from the representation used to reason about it.",
        correct_choice_ids=("system-reality",),
        hints=("Ask which option allows a model to omit features deliberately.",),
        misconception_by_choice=(
            ("model-perfect", "model-is-perfect-copy"),
            ("simulation-experiment", "simulation-equals-experiment"),
        ),
    ),
    AssessmentDefinition(
        "m01-precision-check",
        MODELS_MEASUREMENTS_LESSON.id,
        QuestionKind.MULTIPLE_CHOICE,
        ("m01-measurement",),
        "Correct: the value, unit, and uncertainty match the ruler's stated resolution.",
        "A measurement needs a unit, and its digits should respect the instrument resolution.",
        correct_choice_ids=("honest",),
        hints=("Look for both a unit and an uncertainty consistent with 0.1 cm markings.",),
        misconception_by_choice=(
            ("false-precision", "extra-digits-imply-accuracy"),
            ("no-unit", "quantity-without-unit"),
        ),
    ),
    AssessmentDefinition(
        "m01-graph-check",
        MODELS_MEASUREMENTS_LESSON.id,
        QuestionKind.NUMERIC,
        ("m01-measurement", "m01-representations"),
        "Correct: the graph supports a range of about 40.8 m, without unjustified extra precision.",
        "Check the 45° coordinate, the vertical-axis unit, and the scale before reading the value.",
        expected_numeric_value=40.77,
        canonical_unit="m",
        absolute_tolerance=0.5,
        hints=("Trace vertically from 45° to the curve, then horizontally to the range axis.",),
    ),
)
