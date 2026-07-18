"""Side-effect-free mission evaluation and progress summaries."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from physics_playground.application_callbacks import ApplicationEvent, BadgeEarned, ProgressChanged
from physics_playground.contracts import MissionEvaluation
from physics_playground.missions.definitions import MISSION_DEFINITIONS, MISSIONS_BY_SIMULATION


@dataclass(slots=True)
class MissionProgress:
    completed: set[str] = field(default_factory=set)
    pending_explanations: set[str] = field(default_factory=set)
    attempts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CompletionSummary:
    simulation_id: str
    earned: int
    total: int
    percentage: float


def evaluate_run(
    progress: MissionProgress,
    simulation_id: str,
    evaluations: Iterable[MissionEvaluation],
    publish: Callable[[ApplicationEvent], None] | None = None,
) -> tuple[str, ...]:
    evidence = {item.mission_id: item.completed for item in evaluations}
    earned = []
    for mission in MISSIONS_BY_SIMULATION[simulation_id]:
        qualifies = (
            (mission.id in progress.pending_explanations)
            if mission.completion_rule_id == f"run:{mission.id}"
            and mission.category.value == "Explanation"
            else evidence.get(mission.id, False)
        )
        if not qualifies:
            progress.attempts[mission.id] = progress.attempts.get(mission.id, 0) + 1
            continue
        if any(required not in progress.completed for required in mission.prerequisites):
            continue
        if mission.id not in progress.completed:
            progress.completed.add(mission.id)
            earned.append(mission.id)
        progress.pending_explanations.discard(mission.id)
    earned_ids = tuple(earned)
    if publish is not None and earned_ids:
        for mission_id in earned_ids:
            publish(BadgeEarned(simulation_id, mission_id))
        publish(ProgressChanged(simulation_id, tuple(sorted(progress.completed))))
    return earned_ids


def hint_for(progress: MissionProgress, mission_id: str) -> str:
    mission = MISSION_DEFINITIONS[mission_id]
    if not mission.hints:
        return ""
    index = min(progress.attempts.get(mission_id, 0), len(mission.hints) - 1)
    return mission.hints[index]


def summary(progress: MissionProgress, simulation_id: str) -> CompletionSummary:
    missions = MISSIONS_BY_SIMULATION[simulation_id]
    earned = sum(item.id in progress.completed for item in missions)
    total = len(missions)
    return CompletionSummary(simulation_id, earned, total, earned / total if total else 0)


def overall_percentage(progress: MissionProgress) -> float:
    return len(progress.completed) / len(MISSION_DEFINITIONS) if MISSION_DEFINITIONS else 0
