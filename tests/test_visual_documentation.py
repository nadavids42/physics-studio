from pathlib import Path
import re


ROOT=Path(__file__).parents[1]
GUIDE=ROOT/"docs"/"VISUAL_SYSTEM.md"


def test_readme_links_to_visual_system_guide():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    assert "[docs/VISUAL_SYSTEM.md](docs/VISUAL_SYSTEM.md)" in readme
    assert GUIDE.is_file()


def test_visual_guide_covers_required_authoring_and_migration_topics():
    guide=GUIDE.read_text(encoding="utf-8")
    required=(
        "## Design principles","## Semantic color usage","## Adding a new asset",
        "## Styling a new simulation","## Schematic versus scaled visuals","## Dark mode",
        "## Reduced motion","## Presentation levels","## Animation and performance",
        "## Accessibility","## Pilot examples","## Migration guide for remaining simulations",
    )
    for heading in required:assert heading in guide
    for mode in ("Explore","Compare","Analyze","Model"):assert mode in guide


def test_documented_visual_module_paths_exist():
    guide=GUIDE.read_text(encoding="utf-8")
    paths=set(re.findall(r"((?:visual|canvas|presentation)/[a-z_]+\.py)",guide))
    assert {"visual/tokens.py","visual/assets.py","visual/vectors.py","canvas/player.py","presentation/chart_system.py"}<=paths
    for relative in paths:assert (ROOT/"physics_playground"/relative).is_file(),relative


def test_migration_guide_contains_preservation_and_verification_gates():
    guide=GUIDE.read_text(encoding="utf-8")
    gates=("numerical result arrays and units are unchanged","notebook capture","missions and badges",
           "public builder functions","narrow layouts do not overflow","complete suite")
    for gate in gates:assert gate in guide
