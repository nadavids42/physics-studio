from physics_playground.missions.definitions import MISSION_DEFINITIONS
from physics_playground.models.simulations import Difficulty
from physics_playground.registry import SIMULATION_REGISTRY, SIMULATIONS_BY_ID


def test_registry_has_twenty_two_stable_unique_ids():
    assert len(SIMULATION_REGISTRY) == 22
    assert len(SIMULATIONS_BY_ID) == 22


def test_every_definition_has_complete_home_metadata():
    for item in SIMULATION_REGISTRY:
        assert item.title and item.icon and item.description and item.central_question
        assert item.concepts and isinstance(item.difficulty, Difficulty)
        assert item.badge_count > 0 and item.renderer and item.model_version and item.visual
        assert item.page_module.startswith("physics_playground.")
        assert item.page_module.endswith(".page") or item.page_module.startswith(
            "physics_playground.pages."
        )


def test_badge_counts_match_mission_catalog():
    for item in SIMULATION_REGISTRY:
        actual = sum(
            mission.group == item.mission_group for mission in MISSION_DEFINITIONS.values()
        )
        assert actual == item.badge_count
