import json,sqlite3
from physics_playground.profiles import LocalProfile,ProfileStore,SCHEMA_VERSION
def sample_profile(identifier="p1"):
    return LocalProfile(id=identifier,display_name="Ada",badges_earned=("collision_predict",),trial_notebook={"trials":[],"next_trial_number":1},last_used_simulation="bumper_cars",last_used_parameters={"bumper_cars":{"mass_a_kg":2.0}},favorite_simulation="bumper_cars",total_experiment_count=3,learner_observations=("Momentum stayed constant.",),application_version="1.0.0")
def test_save_and_load(tmp_path):
    store=ProfileStore(tmp_path/"profiles.db");profile=sample_profile();store.save(profile);loaded=store.load(profile.id)
    assert loaded.display_name=="Ada";assert loaded.badges_earned==("collision_predict",);assert loaded.last_used_parameters["bumper_cars"]["mass_a_kg"]==2.0
def test_create_and_list_profiles(tmp_path):
    store=ProfileStore(tmp_path/"profiles.db");a=store.create("Ada");b=store.create("Ben");assert {p.id for p in store.list_profiles()}=={a.id,b.id}
def test_export_and_import_creates_new_identity(tmp_path):
    store=ProfileStore(tmp_path/"profiles.db");profile=sample_profile();store.save(profile);text=store.export_profile(profile.id);imported=store.import_profile(text)
    assert imported.id!=profile.id;assert imported.display_name==profile.display_name;assert imported.badges_earned==profile.badges_earned
def test_reset_preserves_name_and_favorite_only(tmp_path):
    store=ProfileStore(tmp_path/"profiles.db");profile=sample_profile();store.save(profile);reset=store.reset(profile.id)
    assert reset.display_name=="Ada" and reset.favorite_simulation=="bumper_cars";assert reset.badges_earned==() and reset.total_experiment_count==0
def test_schema_migration_from_version_one(tmp_path):
    path=tmp_path/"old.db";payload=json.dumps({"id":"old","display_name":"Old Scientist","badges_earned":["pend_predict"]})
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE profiles (id TEXT PRIMARY KEY, display_name TEXT NOT NULL, payload TEXT NOT NULL)");db.execute("INSERT INTO profiles VALUES (?,?,?)",("old","Old Scientist",payload));db.execute("PRAGMA user_version=1")
    store=ProfileStore(path);loaded=store.load("old")
    assert loaded.display_name=="Old Scientist" and loaded.badges_earned==("pend_predict",)
    with sqlite3.connect(path) as db:assert db.execute("PRAGMA user_version").fetchone()[0]==SCHEMA_VERSION;assert "updated_at" in {row[1] for row in db.execute("PRAGMA table_info(profiles)")}
