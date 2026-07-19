"""Normalized persistence, migration, isolation, and concurrency tests."""

from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest

from physics_playground.learning_store import (
    STORE_SCHEMA_VERSION,
    LearnerData,
    LearnerIdentity,
    SQLiteLearningStore,
)


def record(identifier: str, **values: object) -> dict[str, object]:
    return {"id": identifier, "schema_version": 1, **values}


def sample_data(identifier: str = "learner-1") -> LearnerData:
    return LearnerData(
        LearnerIdentity(identifier, "Ada"),
        {"reduced_motion": True, "schema_version": 1},
        (("lesson-1", {"schema_version": 3, "completed": False}),),
        (record("attempt-1", assessment_id="check-1"),),
        (record("trial-1", simulation_id="cannonball"),),
        (record("note-1", lesson_id="lesson-1", response="Evidence"),),
        ("cannon_predict",),
        {"favorite_simulation": "cannonball"},
        (record("evidence-1", objective_id="objective-1"),),
    )


def test_high_growth_domains_are_normalized_and_round_trip(tmp_path) -> None:
    store = SQLiteLearningStore(tmp_path / "learning.db")
    expected = sample_data()
    store.save(expected)
    assert store.load(expected.identity.id) == expected
    with store.connect() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == STORE_SCHEMA_VERSION
        assert db.execute("SELECT count(*) FROM assessment_attempts").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM experiment_trials").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM notebook_entries").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM lesson_progress").fetchone()[0] == 1


def test_export_import_round_trip_uses_versioned_bundle_and_new_identity(tmp_path) -> None:
    store = SQLiteLearningStore(tmp_path / "learning.db")
    store.save(sample_data())
    exported = store.export_learner("learner-1")
    assert json.loads(exported)["export_schema_version"] == 1
    imported = store.import_learner(exported, new_id="learner-2")
    assert imported.identity.id == "learner-2"
    assert imported.assessment_attempts[0]["id"] == "attempt-1"
    assert store.load("learner-2") == imported


def test_invalid_write_rolls_back_the_entire_transaction(tmp_path) -> None:
    store = SQLiteLearningStore(tmp_path / "learning.db")
    original = sample_data()
    store.save(original)
    invalid = LearnerData(
        original.identity,
        original.preferences,
        assessment_attempts=({"schema_version": 1},),
    )
    with pytest.raises(ValueError, match="string id"):
        store.save(invalid)
    assert store.load(original.identity.id) == original


def test_one_malformed_row_is_quarantined_without_losing_learner(tmp_path) -> None:
    store = SQLiteLearningStore(tmp_path / "learning.db")
    store.save(sample_data())
    with store.connect() as db:
        db.execute(
            "INSERT INTO assessment_attempts VALUES(?,?,?,?,?)".replace("?,?,?,?,?", "?,?,?,1"),
            ("learner-1", "bad", "{not-json"),
        )
        db.commit()
    loaded = store.load("learner-1")
    assert loaded.identity.display_name == "Ada"
    assert tuple(item["id"] for item in loaded.assessment_attempts) == ("attempt-1",)
    with store.connect() as db:
        assert (
            db.execute(
                "SELECT count(*) FROM rejected_records WHERE learner_id='learner-1'"
            ).fetchone()[0]
            >= 1
        )


def test_legacy_profile_migration_skips_bad_child_records(tmp_path) -> None:
    path = tmp_path / "legacy.db"
    payload = {
        "id": "legacy",
        "display_name": "Grace",
        "assessment_attempts": [record("good"), "broken"],
        "trial_notebook": {"trials": [record("trial"), {"missing": "id"}]},
    }
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TABLE profiles(id TEXT PRIMARY KEY,display_name TEXT NOT NULL,payload TEXT NOT NULL,updated_at TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO profiles VALUES(?,?,?,?)", ("legacy", "Grace", json.dumps(payload), "")
        )
        db.execute("PRAGMA user_version=3")
    store = SQLiteLearningStore(path)
    loaded = store.load("legacy")
    assert loaded.identity.display_name == "Grace"
    assert tuple(item["id"] for item in loaded.assessment_attempts) == ("good",)
    assert tuple(item["id"] for item in loaded.experiment_trials) == ("trial",)
    with store.connect() as db:
        assert db.execute("SELECT count(*) FROM rejected_records").fetchone()[0] == 2


def test_concurrent_writes_are_serialized_without_lost_learners(tmp_path) -> None:
    path = tmp_path / "learning.db"
    SQLiteLearningStore(path)

    def write(index: int) -> None:
        SQLiteLearningStore(path).save(sample_data(f"learner-{index}"))

    with ThreadPoolExecutor(max_workers=6) as pool:
        tuple(pool.map(write, range(20)))
    store = SQLiteLearningStore(path)
    assert len(store.list_identities()) == 20
    assert all(store.load(f"learner-{index}").experiment_trials for index in range(20))


def test_concurrent_attempt_appends_do_not_rewrite_or_lose_history(tmp_path) -> None:
    path = tmp_path / "learning.db"
    store = SQLiteLearningStore(path)
    store.save(sample_data())

    def append(index: int) -> None:
        SQLiteLearningStore(path).append_assessment_attempt(
            "learner-1", record(f"attempt-{index}", assessment_id="check")
        )

    with ThreadPoolExecutor(max_workers=6) as pool:
        tuple(pool.map(append, range(2, 22)))
    attempts = SQLiteLearningStore(path).get_assessment_attempts("learner-1")
    assert {item["id"] for item in attempts} == {
        "attempt-1",
        *(f"attempt-{index}" for index in range(2, 22)),
    }


def test_import_drops_invalid_child_without_rejecting_valid_export(tmp_path) -> None:
    store = SQLiteLearningStore(tmp_path / "learning.db")
    store.save(sample_data())
    exported = json.loads(store.export_learner("learner-1"))
    exported["learner"]["assessment_attempts"].append({"missing": "id"})
    imported = store.import_learner(json.dumps(exported), new_id="safe-import")
    assert tuple(item["id"] for item in imported.assessment_attempts) == ("attempt-1",)
