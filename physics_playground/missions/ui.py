"""Streamlit mission UI backed by structured mission definitions and service."""

from __future__ import annotations

import streamlit as st

from physics_playground.application_callbacks import BadgeEarned, ProgressChanged, publish
from physics_playground.contracts import MissionEvaluation
from physics_playground.missions.definitions import (
    MISSION_DEFINITIONS,
    MISSIONS_BY_SIMULATION,
)
from physics_playground.missions.service import (
    MissionProgress,
    evaluate_run,
    hint_for,
    overall_percentage,
    summary,
)
from physics_playground.presentation.formatting import friendly_minutes, friendly_speed
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.state_keys import SHARED_STATE_KEYS, migrate_legacy_keys

MISSION_LABELS = {mid: item.title for mid, item in MISSION_DEFINITIONS.items()}
MISSION_GROUPS = {
    item.mission_group: [mission.id for mission in MISSIONS_BY_SIMULATION[item.id]]
    for item in SIMULATION_REGISTRY
}
GROUP_TO_SIMULATION = {item.mission_group: item.id for item in SIMULATION_REGISTRY}


def init_missions():
    migrate_legacy_keys(st.session_state)
    completed_key = SHARED_STATE_KEYS.missions_completed
    progress_key = SHARED_STATE_KEYS.missions_progress
    if completed_key not in st.session_state:
        st.session_state[completed_key] = set()
    if progress_key not in st.session_state:
        st.session_state[progress_key] = MissionProgress(
            completed=set(st.session_state[completed_key])
        )
    else:
        st.session_state[progress_key].completed.update(st.session_state[completed_key])
    st.session_state[completed_key] = st.session_state[progress_key].completed


def _celebrate(mission_id, celebrate=True):
    mission = MISSION_DEFINITIONS[mission_id]
    prefix = "Hidden achievement earned" if mission.hidden else "Achievement earned"
    st.toast(f"{prefix}: {mission.title}!")
    if celebrate:
        st.balloons()


def complete(mission_id: str, celebrate: bool = True, experiment_ran: bool = False):
    """Compatibility API. Run-based missions require explicit run evidence."""
    init_missions()
    mission = MISSION_DEFINITIONS[mission_id]
    if not experiment_ran:
        return False
    if any(
        required not in st.session_state[SHARED_STATE_KEYS.missions_progress].completed
        for required in mission.prerequisites
    ):
        return False
    if mission_id not in st.session_state[SHARED_STATE_KEYS.missions_progress].completed:
        st.session_state[SHARED_STATE_KEYS.missions_progress].completed.add(mission_id)
        _celebrate(mission_id, celebrate)
        publish(BadgeEarned(mission.simulation_id, mission_id))
        publish(
            ProgressChanged(
                mission.simulation_id,
                tuple(sorted(st.session_state[SHARED_STATE_KEYS.missions_progress].completed)),
            )
        )
        return True
    return False


def process_run(simulation_id: str, evaluations: tuple[MissionEvaluation, ...]) -> tuple[str, ...]:
    init_missions()
    earned = evaluate_run(
        st.session_state[SHARED_STATE_KEYS.missions_progress],
        simulation_id,
        evaluations,
        publish,
    )
    for mission_id in earned:
        _celebrate(mission_id)
    return earned


def is_done(mission_id: str) -> bool:
    init_missions()
    return mission_id in st.session_state[SHARED_STATE_KEYS.missions_progress].completed


def mission_checklist(group: str):
    init_missions()
    simulation_id = GROUP_TO_SIMULATION[group]
    status = summary(st.session_state[SHARED_STATE_KEYS.missions_progress], simulation_id)
    st.markdown(f"#### Progress — {status.earned}/{status.total} ({status.percentage:.0%})")
    for mission in MISSIONS_BY_SIMULATION[simulation_id]:
        done = mission.id in st.session_state[SHARED_STATE_KEYS.missions_progress].completed
        if mission.hidden and not done:
            continue
        title = mission.title if not mission.hidden else f"Hidden: {mission.title}"
        state = "Complete" if done else "Not complete"
        st.markdown(f"**{state}: {title}** — {mission.description}")
        if not done:
            blocked = [
                MISSION_DEFINITIONS[item].title
                for item in mission.prerequisites
                if item not in st.session_state[SHARED_STATE_KEYS.missions_progress].completed
            ]
            if blocked:
                st.caption(f"First complete: {', '.join(blocked)}")
            else:
                hint = hint_for(st.session_state[SHARED_STATE_KEYS.missions_progress], mission.id)
                if hint:
                    st.caption(f"Hint: {hint}")


def sidebar_badges():
    init_missions()
    progress = st.session_state[SHARED_STATE_KEYS.missions_progress]
    percentage = overall_percentage(progress)
    st.progress(
        percentage,
        text=f"{len(progress.completed)} of {len(MISSION_DEFINITIONS)} badges · {percentage:.0%}",
    )
    for item in SIMULATION_REGISTRY:
        status = summary(progress, item.id)
        st.caption(f"{item.title}: {status.earned}/{status.total} ({status.percentage:.0%})")


def prediction_quiz(key, question, options, correct_index, reveal_text, mission_id=None):
    init_missions()
    guess_key = f"{key}_guess"
    revealed_key = f"{key}_revealed"
    st.markdown(f"### Make a prediction\n**{question}**")
    guess = st.radio(
        "Your guess:", options, index=None, key=guess_key, label_visibility="collapsed"
    )
    if not st.session_state.get(revealed_key, False):
        if st.button(
            "Submit prediction", key=f"{key}_lock", disabled=guess is None, type="primary"
        ):
            st.session_state[revealed_key] = True
            if mission_id:
                st.session_state[SHARED_STATE_KEYS.missions_progress].pending_explanations.add(
                    mission_id
                )
            st.rerun()
        if guess is None:
            st.caption("Select an answer before submitting your prediction.")
        return False
    if (
        mission_id
        and mission_id not in st.session_state[SHARED_STATE_KEYS.missions_progress].completed
    ):
        st.session_state[SHARED_STATE_KEYS.missions_progress].pending_explanations.add(mission_id)
    if guess == options[correct_index]:
        st.success(f"**Correct.** {reveal_text}")
    else:
        st.warning(f"**Compare your prediction with the result.** {reveal_text}")
    if (
        mission_id
        and mission_id not in st.session_state[SHARED_STATE_KEYS.missions_progress].completed
    ):
        st.caption("Run the experiment to earn the explanation badge.")
    return True


# Deprecated compatibility export. Unverified real-world analogy values were removed.
SPEED_THINGS: tuple[()] = ()


def fun_speed(mps):
    """Compatibility name for verified speed-unit formatting."""

    return friendly_speed(mps)


def fun_time_minutes(minutes):
    """Compatibility name for verified elapsed-time formatting."""

    return friendly_minutes(minutes)
