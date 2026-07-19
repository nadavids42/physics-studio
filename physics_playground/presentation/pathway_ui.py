"""Streamlit renderer for typed educational pathways."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

from physics_playground.application_callbacks import NotebookChanged, publish
from physics_playground.education.assessments import (
    AssessmentAttempt,
    AssessmentResponse,
    GradingStatus,
    deterministic_variant_id,
    submit_response,
)
from physics_playground.education.audience import (
    AudienceLevel,
    AudiencePreferences,
    MathematicalDepth,
    VisualDensity,
    applies_at_depth,
)
from physics_playground.education.catalog import ASSESSMENTS_BY_ID, LESSONS_BY_ID
from physics_playground.education.models import (
    ActivityPhase,
    CheckpointQuestion,
    DiagramSpec,
    EducationEventKind,
    EducationProgressEvent,
    GuidedDerivation,
    Lesson,
    MisconceptionCallout,
    PrerequisiteKind,
    QuestionKind,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.education.progress import MINIMUM_REFLECTION_LENGTH, PathwayProgress
from physics_playground.presentation.accessibility_ui import get_accessibility_settings
from physics_playground.presentation.profile_ui import get_notebook
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key, simulation_key

FIGURE_ROOT = Path(__file__).parents[1] / "static" / "figures"


def _requirements(
    lesson: Lesson, depth: MathematicalDepth
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    visible_sections = tuple(
        section for section in lesson.sections if applies_at_depth(section, depth)
    )
    visible_activity_ids = {
        component.id
        for section in visible_sections
        for component in section.components
        if isinstance(component, SimulationActivity) and applies_at_depth(component, depth)
    }
    activities = tuple(
        activity.id for activity in lesson.activity_sequence if activity.id in visible_activity_ids
    )
    checkpoints = tuple(
        component.id
        for section in visible_sections
        for component in section.components
        if isinstance(component, CheckpointQuestion) and applies_at_depth(component, depth)
    )
    return activities, checkpoints


def _progress_map() -> dict[str, PathwayProgress]:
    value = st.session_state.setdefault(SHARED_STATE_KEYS.education_progress, {})
    if not isinstance(value, dict):
        value = {}
        st.session_state[SHARED_STATE_KEYS.education_progress] = value
    return value


def get_pathway_progress(lesson: Lesson) -> PathwayProgress:
    progress = _progress_map().get(lesson.id)
    if not isinstance(progress, PathwayProgress):
        progress = PathwayProgress(lesson.id)
        _progress_map()[lesson.id] = progress
    return progress


def _save_progress(
    progress: PathwayProgress,
    *,
    kind: EducationEventKind,
    activity_id: str | None = None,
    checkpoint_id: str | None = None,
) -> None:
    _progress_map()[progress.lesson_id] = progress
    publish(
        EducationProgressEvent(
            id=uuid4().hex,
            kind=EducationEventKind.LESSON_COMPLETED if progress.completed else kind,
            learner_id=str(st.session_state.get(SHARED_STATE_KEYS.profiles_active_id, "session")),
            lesson_id=progress.lesson_id,
            occurred_at=datetime.now(UTC),
            activity_id=activity_id,
            checkpoint_id=checkpoint_id,
            completed=progress.completed,
        )
    )


def _learner_id() -> str:
    return str(st.session_state.get(SHARED_STATE_KEYS.profiles_active_id, "session"))


def _render_diagram(diagram: DiagramSpec) -> None:
    """Render a versioned figure with a text equivalent and semantic caption."""

    path = FIGURE_ROOT / f"{diagram.asset_id}.svg"
    st.markdown(f"#### Figure: {diagram.caption}")
    if path.is_file():
        st.image(str(path), caption=diagram.caption)
    else:
        st.info("The visual figure is unavailable; use the description below.")
    st.caption(f"Figure description: {diagram.alt_text}")


def _render_worked_example(example: WorkedExample, preferences: AudiencePreferences) -> None:
    st.markdown(f"#### Worked example: {example.title}")
    st.write(example.prompt)
    st.markdown("**Known values**")
    for known in example.known_values:
        value = known.display_value or f"{known.value:g} {known.quantity.unit}"
        st.markdown(f"- {known.quantity.symbol} ({known.quantity.name}) = {value}")
    st.markdown(
        f"**Unknown:** {example.unknown.symbol}, {example.unknown.name} ({example.unknown.unit})"
    )
    st.markdown("**Symbolic reasoning**")
    reasoning = (
        example.symbolic_reasoning[:1]
        if preferences.mathematical_depth is MathematicalDepth.CONCEPTUAL
        else example.symbolic_reasoning
    )
    for step in reasoning:
        st.latex(step.expression)
        st.caption(step.explanation)
    st.markdown("**Substitute only after the symbolic setup**")
    for substitution in example.substitutions:
        st.code(f"{substitution.expression}\n{substitution.result}")
    st.info(f"Unit check: {example.unit_check}")
    st.success(example.final_answer)
    st.write(example.final_interpretation)
    if preferences.mathematical_depth is MathematicalDepth.EXTENDED:
        st.caption(
            "Extension: compare this analytic value with progressively smaller numerical time steps before attributing a discrepancy to the physical model."
        )


def _render_derivation(derivation: GuidedDerivation) -> None:
    st.markdown(f"#### Guided derivation: {derivation.title}")
    st.write(derivation.goal)
    st.markdown("**Assumptions used in this derivation**")
    for assumption in derivation.assumptions:
        st.markdown(f"- {assumption}")
    for step in derivation.steps:
        with st.expander(f"Reveal step {step.reveal_order}: {step.prompt}"):
            if step.hint:
                st.caption(f"Hint: {step.hint}")
            st.latex(step.expression)
            st.write(step.explanation)
    st.info(derivation.conclusion)


def _render_checkpoint(
    lesson: Lesson,
    question: CheckpointQuestion,
    progress: PathwayProgress,
    preferences: AudiencePreferences,
    required_section_ids: tuple[str, ...],
) -> PathwayProgress:
    definition = ASSESSMENTS_BY_ID[question.id]
    attempts_key = feature_key("education", "assessment_attempts")
    attempts = st.session_state.setdefault(attempts_key, [])
    prior_attempts = tuple(
        item
        for item in attempts
        if isinstance(item, AssessmentAttempt) and item.assessment_id == question.id
    )
    variant_id = deterministic_variant_id(
        definition,
        learner_id=_learner_id(),
        attempt_number=len(prior_attempts) + 1,
    )
    variant = next((item for item in question.variants if item.id == variant_id), None)
    prompt = variant.prompt if variant else question.prompt
    choices = variant.choices if variant else question.choices
    unit_options = variant.unit_options if variant else question.unit_options
    st.markdown(f"#### Checkpoint: {prompt}")
    if prior_attempts:
        st.caption(
            f"Attempt history: {len(prior_attempts)} submitted · "
            f"latest status {prior_attempts[-1].status.value.replace('_', ' ')}"
        )
    if question.id in progress.completed_checkpoint_ids:
        st.success("Checkpoint complete.")
        st.write(definition.success_feedback)
        return progress
    answer_key = feature_key("education", f"{lesson.id}.{question.id}.answer")
    response: AssessmentResponse
    if question.kind is QuestionKind.MULTIPLE_CHOICE:
        answer = st.radio(
            "Choose an answer",
            [choice.id for choice in choices],
            format_func={choice.id: choice.text for choice in choices}.get,
            key=answer_key,
        )
        response = AssessmentResponse(selected_choice_ids=(answer,))
    elif question.kind is QuestionKind.MULTIPLE_SELECT:
        selected = st.multiselect(
            "Select all answers that apply",
            [choice.id for choice in choices],
            format_func={choice.id: choice.text for choice in choices}.get,
            key=answer_key,
        )
        response = AssessmentResponse(selected_choice_ids=tuple(selected))
    elif question.kind is QuestionKind.NUMERIC:
        raw_value = st.text_input("Numeric response", key=answer_key)
        selected_unit = st.selectbox(
            "Response unit",
            unit_options,
            key=feature_key("education", f"{lesson.id}.{question.id}.unit"),
        )
        try:
            numeric_value = float(raw_value)
        except ValueError:
            numeric_value = None
        response = AssessmentResponse(numeric_value=numeric_value, unit=selected_unit)
    else:
        text = st.text_area(
            "Constructed response for self-review",
            key=answer_key,
            help="The system records this response but does not claim to grade its reasoning.",
        )
        response = AssessmentResponse(text=text)
    if st.button("Check answer", key=feature_key("education", f"{question.id}.submit")):
        result = submit_response(
            definition,
            response,
            learner_id=_learner_id(),
            attempt_id=uuid4().hex,
            submitted_at=datetime.now(UTC),
            prior_attempts=prior_attempts,
            variant_id=variant_id,
        )
        attempts.append(result.attempt)
        if result.evidence:
            evidence_key = feature_key("education", "objective_evidence")
            st.session_state.setdefault(evidence_key, []).extend(result.evidence)
        if result.attempt.status in {GradingStatus.CORRECT, GradingStatus.SELF_REVIEW}:
            activities, checkpoints = _requirements(lesson, preferences.mathematical_depth)
            updated = progress.complete_checkpoint(
                question.id,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
                required_section_ids=required_section_ids,
                attempt_id=result.attempt.id,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.CHECKPOINT_ATTEMPTED,
                checkpoint_id=question.id,
            )
            st.success(result.feedback)
            for mastery in result.mastery:
                st.caption(
                    f"Objective {mastery.objective_id}: assessment status "
                    f"{mastery.status.value.replace('_', ' ')}"
                )
            return updated
        st.error(result.feedback)
        if result.hint:
            st.info(f"Hint: {result.hint}")
        if result.attempt.misconception_tags:
            st.caption("Review focus: " + ", ".join(result.attempt.misconception_tags))
    return progress


def _render_activity(
    lesson: Lesson,
    activity: SimulationActivity,
    progress: PathwayProgress,
    preferences: AudiencePreferences,
    required_section_ids: tuple[str, ...],
) -> PathwayProgress:
    complete = activity.id in progress.completed_activity_ids
    st.markdown(f"#### {activity.phase.value.title()}: {activity.title}")
    for index, instruction in enumerate(activity.instructions, start=1):
        prefix = f"{index}." if preferences.audience is AudienceLevel.EXPLORER else "-"
        st.markdown(f"{prefix} {instruction}")
    if activity.observation_prompt:
        st.info(activity.observation_prompt)
    if preferences.visual_density is VisualDensity.DETAILED and activity.expected_reflection:
        st.caption(f"What your reflection should include: {activity.expected_reflection}")
    activities, checkpoints = _requirements(lesson, preferences.mathematical_depth)
    if activity.phase is ActivityPhase.PREDICTION:
        if progress.prediction is not None:
            st.success(f"Saved prediction: {progress.prediction}")
            if st.button(
                "Reset prediction",
                key=feature_key("education", f"{lesson.id}.reset_prediction"),
            ):
                updated = progress.reset_prediction(activity.id)
                _save_progress(
                    updated,
                    kind=EducationEventKind.ACTIVITY_COMPLETED,
                    activity_id=activity.id,
                )
                return updated
            return progress
        prediction_key = feature_key("education", f"{lesson.id}.prediction")
        prediction = st.text_area("Record your prediction and physical reason", key=prediction_key)
        st.caption(
            f"Write at least {MINIMUM_REFLECTION_LENGTH} characters — this is your own "
            "reasoning, not a graded answer."
        )
        if st.button(
            "Save prediction",
            disabled=len(prediction.strip()) < MINIMUM_REFLECTION_LENGTH,
            key=feature_key("education", f"{lesson.id}.save_prediction"),
        ):
            updated = progress.save_prediction(
                prediction,
                activity.id,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
                required_section_ids=required_section_ids,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.ACTIVITY_COMPLETED,
                activity_id=activity.id,
            )
            return updated
        return progress
    if activity.phase is ActivityPhase.REFLECTION:
        reflection_key = feature_key("education", f"{lesson.id}.reflection")
        initial = progress.reflection or ""
        if reflection_key not in st.session_state:
            st.session_state[reflection_key] = initial
        response = st.text_area("Notebook reflection", key=reflection_key)
        st.caption(f"Write at least {MINIMUM_REFLECTION_LENGTH} characters, not a placeholder.")
        if complete:
            st.success("Reflection saved to your notebook.")
        if st.button(
            "Save notebook reflection",
            disabled=len(response.strip()) < MINIMUM_REFLECTION_LENGTH,
            key=feature_key("education", f"{lesson.id}.save_reflection"),
        ):
            updated = progress.save_reflection(
                response,
                activity.id,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
                required_section_ids=required_section_ids,
            )
            reflection = get_notebook().save_lesson_reflection(
                lesson_id=lesson.id,
                prompt=activity.observation_prompt,
                response=response,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.ACTIVITY_COMPLETED,
                activity_id=activity.id,
            )
            publish(NotebookChanged(reflection.id))
            return updated
        return progress
    if activity.mode is not None and st.button(
        f"Open {activity.mode.value} mode",
        key=feature_key("education", f"{activity.id}.open_mode"),
    ):
        st.session_state[simulation_key(activity.simulation_id, "learning_mode")] = (
            activity.mode.value
        )
        st.toast(f"{activity.mode.value} mode selected below.")
    if complete:
        st.success("Activity complete.")
    elif activity.evidence_prompt:
        response_key = feature_key("education", f"{lesson.id}.{activity.id}.reflection")
        saved = dict(progress.activity_responses).get(activity.id, "")
        if response_key not in st.session_state:
            st.session_state[response_key] = saved
        response = st.text_area(activity.evidence_prompt, key=response_key)
        st.caption(f"Write at least {MINIMUM_REFLECTION_LENGTH} characters, not a placeholder.")
        if st.button(
            "Save observation reflection",
            disabled=len(response.strip()) < MINIMUM_REFLECTION_LENGTH,
            key=feature_key("education", f"{activity.id}.complete"),
        ):
            updated = progress.save_activity_response(
                activity.id,
                response,
                required_activity_ids=activities,
                required_checkpoint_ids=checkpoints,
                required_section_ids=required_section_ids,
            )
            _save_progress(
                updated,
                kind=EducationEventKind.ACTIVITY_COMPLETED,
                activity_id=activity.id,
            )
            return updated
    elif st.button(
        "Mark activity complete",
        key=feature_key("education", f"{activity.id}.complete"),
    ):
        updated = progress.complete_activity(
            activity.id,
            required_activity_ids=activities,
            required_checkpoint_ids=checkpoints,
            required_section_ids=required_section_ids,
        )
        _save_progress(
            updated,
            kind=EducationEventKind.ACTIVITY_COMPLETED,
            activity_id=activity.id,
        )
        return updated
    return progress


def _set_lesson_section(key: str, section_id: str) -> None:
    st.session_state[key] = section_id


def _complete_and_navigate(
    lesson: Lesson,
    progress: PathwayProgress,
    section_id: str,
    next_section_id: str | None,
    required_activity_ids: tuple[str, ...],
    required_checkpoint_ids: tuple[str, ...],
    required_section_ids: tuple[str, ...],
    navigation_key: str,
) -> None:
    updated = progress.complete_section(
        section_id,
        required_activity_ids=required_activity_ids,
        required_checkpoint_ids=required_checkpoint_ids,
        required_section_ids=required_section_ids,
        next_section_id=next_section_id,
    )
    _save_progress(updated, kind=EducationEventKind.SECTION_COMPLETED)
    st.session_state[navigation_key] = next_section_id or section_id


def _unmet_lesson_prerequisites(lesson: Lesson) -> tuple[Lesson, ...]:
    progress_by_lesson = _progress_map()
    return tuple(
        LESSONS_BY_ID[prerequisite.reference_id]
        for prerequisite in lesson.prerequisites
        if prerequisite.required
        and prerequisite.kind is PrerequisiteKind.LESSON
        and prerequisite.reference_id in LESSONS_BY_ID
        and not (
            prerequisite.reference_id in progress_by_lesson
            and progress_by_lesson[prerequisite.reference_id].completed
        )
    )


def _open_prerequisite_lesson(prerequisite: Lesson) -> None:
    simulation_id = prerequisite.simulation_ids[0]
    st.session_state[SHARED_STATE_KEYS.navigation_active] = simulation_id
    st.session_state[SHARED_STATE_KEYS.navigation_active_lesson] = prerequisite.id
    st.query_params["simulation"] = simulation_id
    st.query_params["lesson"] = prerequisite.id


def _render_locked_lesson(lesson: Lesson, unmet: tuple[Lesson, ...]) -> None:
    st.header(f"Guided lesson: {lesson.title}")
    st.warning(
        "This lesson unlocks after you complete: "
        + ", ".join(prerequisite.title for prerequisite in unmet)
    )
    for prerequisite in unmet:
        st.button(
            f"Open {prerequisite.title}",
            key=feature_key("education", f"open-prerequisite-{lesson.id}-{prerequisite.id}"),
            on_click=_open_prerequisite_lesson,
            args=(prerequisite,),
        )


def render_learning_pathway(lesson: Lesson) -> None:
    """Render orientation or one resumable lesson section at a time."""

    unmet_prerequisites = _unmet_lesson_prerequisites(lesson)
    if unmet_prerequisites:
        _render_locked_lesson(lesson, unmet_prerequisites)
        return

    progress = get_pathway_progress(lesson)
    preferences = get_accessibility_settings().instructional
    visible_sections = tuple(
        section
        for section in lesson.sections
        if applies_at_depth(section, preferences.mathematical_depth)
    )
    section_ids = tuple(section.id for section in visible_sections)
    activities, checkpoints = _requirements(lesson, preferences.mathematical_depth)
    completed_steps = len(progress.completed_activity_ids) + len(progress.completed_checkpoint_ids)
    total_steps = len(activities) + len(checkpoints)
    navigation_key = feature_key("education", f"{lesson.id}.section")
    if navigation_key not in st.session_state:
        incomplete = next(
            (item for item in section_ids if item not in progress.completed_section_ids),
            section_ids[-1],
        )
        st.session_state[navigation_key] = (
            progress.last_section_id
            if progress.last_section_id in section_ids
            else incomplete
            if progress.completed_section_ids
            else "orientation"
        )

    st.markdown(
        """
        <style>
        .physics-lesson-status {padding:.65rem .8rem;border:1px solid #9aa5b1;border-radius:.5rem;}
        @media (max-width: 640px) {
          .physics-lesson-status {padding:.5rem;font-size:.95rem;}
          div[data-testid="stImage"] img {width:100%;height:auto;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.header(f"Guided lesson: {lesson.title}")
    st.caption(
        f"About {lesson.estimated_minutes} minutes · lesson navigation is separate from "
        "Explore, Compare, Analyze, and Model simulation modes"
    )
    st.progress(
        len(progress.completed_section_ids) / len(section_ids) if section_ids else 0,
        text=(
            f"Lesson status: {len(progress.completed_section_ids)}/{len(section_ids)} sections · "
            f"{completed_steps}/{total_steps} required activities and checkpoints"
        ),
    )
    labels = {"orientation": "Lesson orientation"}
    labels.update(
        {
            section.id: (
                f"Completed — {section.title}"
                if section.id in progress.completed_section_ids
                else section.title
            )
            for section in visible_sections
        }
    )
    selected = st.selectbox(
        "Lesson navigation",
        ("orientation", *section_ids),
        format_func=labels.get,
        key=navigation_key,
        help="Choose a lesson section. Simulation modes are selected in the workspace below.",
    )

    if selected == "orientation":
        introduction = {
            AudienceLevel.EXPLORER: (
                "Begin with the path you can observe, predict before revealing results, and use "
                "the equation to explain the evidence."
            ),
            AudienceLevel.CORE: lesson.summary,
            AudienceLevel.ADVANCED: (
                "Connect trajectory evidence to the analytic model, then test its assumptions "
                "and numerical limits."
            ),
        }[preferences.audience]
        st.subheader("Orientation")
        st.write(introduction)
        st.markdown("### Prerequisites")
        for prerequisite in lesson.prerequisites:
            st.markdown(f"- {prerequisite.rationale}")
        st.markdown("### Learning objectives")
        for objective in lesson.objectives:
            st.markdown(f"- {objective.statement}")
            st.caption(f"Evidence of mastery: {objective.evidence}")
        first_section = next(
            (item for item in section_ids if item not in progress.completed_section_ids),
            section_ids[0],
        )
        st.button(
            "Begin lesson" if not progress.completed_section_ids else "Resume lesson",
            type="primary",
            on_click=_set_lesson_section,
            args=(navigation_key, first_section),
        )
        return

    section_index = section_ids.index(selected)
    section = visible_sections[section_index]
    st.subheader(f"Section {section_index + 1} of {len(section_ids)}: {section.title}")
    status = "complete" if section.id in progress.completed_section_ids else "in progress"
    st.markdown(
        f'<p class="physics-lesson-status" role="status">Section status: {status}.</p>',
        unsafe_allow_html=True,
    )
    st.write(section.narrative)
    for component in section.components:
        if not applies_at_depth(component, preferences.mathematical_depth):
            continue
        if isinstance(component, DiagramSpec):
            _render_diagram(component)
        elif isinstance(component, SimulationActivity):
            progress = _render_activity(lesson, component, progress, preferences, section_ids)
        elif isinstance(component, GuidedDerivation):
            _render_derivation(component)
        elif isinstance(component, WorkedExample):
            _render_worked_example(component, preferences)
        elif isinstance(component, MisconceptionCallout):
            st.warning(
                f"Common misconception: {component.misconception}\n\n"
                f"Correction: {component.correction}"
            )
            if component.diagnostic_prompt:
                st.caption(f"Diagnostic question: {component.diagnostic_prompt}")
        elif isinstance(component, CheckpointQuestion):
            progress = _render_checkpoint(lesson, component, progress, preferences, section_ids)

    section_activity_ids = {
        component.id
        for component in section.components
        if isinstance(component, SimulationActivity)
        and applies_at_depth(component, preferences.mathematical_depth)
    }
    section_checkpoint_ids = {
        component.id
        for component in section.components
        if isinstance(component, CheckpointQuestion)
        and applies_at_depth(component, preferences.mathematical_depth)
    }
    section_ready = section_activity_ids <= set(
        progress.completed_activity_ids
    ) and section_checkpoint_ids <= set(progress.completed_checkpoint_ids)
    if not section_ready:
        st.info("Complete this section's activity or checkpoint before continuing.")
    if section_index:
        st.button(
            "Previous section",
            on_click=_set_lesson_section,
            args=(navigation_key, section_ids[section_index - 1]),
        )
    next_section_id = (
        section_ids[section_index + 1] if section_index + 1 < len(section_ids) else None
    )
    st.button(
        "Continue to next section" if next_section_id else "Complete lesson",
        type="primary",
        disabled=not section_ready,
        on_click=_complete_and_navigate,
        args=(
            lesson,
            progress,
            section.id,
            next_section_id,
            activities,
            checkpoints,
            section_ids,
            navigation_key,
        ),
    )
    if progress.completed:
        st.success("Lesson complete. Your progress and responses are saved.")
        st.subheader("Recommended next step")
        st.write(lesson.next_lesson_title)
    else:
        st.caption("Your current section, responses, and completion status are saved for resume.")
    st.divider()
    st.subheader("Simulation workspace")
    st.caption(
        "Activity buttons select a simulation mode below; lesson sections and simulation modes "
        "remain independent navigation controls."
    )
