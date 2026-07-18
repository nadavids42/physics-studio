"""Framework-neutral trial history for exploration and comparisons."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import uuid4

from physics_playground.contracts import ContractResult, ParameterSet
from physics_playground.serialization import dumps

P = TypeVar("P", bound=ParameterSet)


@dataclass(frozen=True, slots=True)
class Trial(Generic[P]):
    id: str
    created_at: str
    result: ContractResult[P]
    label: str | None = None


@dataclass(slots=True)
class TrialHistory(Generic[P]):
    """In-memory history that can later be stored in ``st.session_state``."""

    simulation_id: str
    trials: list[Trial[P]] = field(default_factory=list)

    def add(self, result: ContractResult[P], label: str | None = None) -> Trial[P]:
        if result.simulation_id != self.simulation_id:
            raise ValueError("Trial result does not belong to this history.")
        trial = Trial(
            id=uuid4().hex,
            created_at=datetime.now(UTC).isoformat(),
            result=result,
            label=label,
        )
        self.trials.append(trial)
        return trial

    def get(self, trial_id: str) -> Trial[P]:
        for trial in self.trials:
            if trial.id == trial_id:
                return trial
        raise KeyError(f"Unknown trial: {trial_id}")

    def to_json(self, *, indent: int | None = None) -> str:
        return dumps(self, indent=indent)
