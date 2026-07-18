from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).parents[1]
DOCUMENTS = (
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CHANGELOG.md",
    ROOT / "docs" / "ARCHITECTURE.md",
    ROOT / "docs" / "EXPANSION_ARCHITECTURE.md",
)


def test_required_open_source_documents_exist() -> None:
    for path in (*DOCUMENTS, ROOT / "LICENSE"):
        assert path.is_file(), f"Missing contributor document: {path.relative_to(ROOT)}"


def test_local_markdown_links_resolve() -> None:
    for source in DOCUMENTS:
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", source.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            relative_target = target.split("#", 1)[0]
            assert (source.parent / relative_target).resolve().exists(), (
                f"Broken link in {source.relative_to(ROOT)}: {target}"
            )


def test_readme_has_current_paths_and_no_historical_changelog_body() -> None:
    readme = (ROOT / "README.md").read_text()
    for stale_reference in (
        "upload/",
        "seven-item",
        "All 25 original achievements",
        "tests/models/test_magnetic_forces.py",
        "tests/canvas/test_vector_diagram.py",
    ):
        assert stale_reference not in readme
    assert "CHANGELOG.md" in readme
    assert "docs/EXPANSION_ARCHITECTURE.md" in readme


def test_documented_test_paths_exist() -> None:
    expected_paths = (
        "tests/canvas",
        "tests/test_visual_system.py",
        "tests/test_visual_regression.py",
        "tests/test_expansion_architecture.py",
        "tests/test_cross_simulation_integration.py",
        "tests/test_expansion_widget_keys.py",
        "tests/test_registry.py",
    )
    assert all((ROOT / path).exists() for path in expected_paths)


def test_package_metadata_declares_apache_license() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert metadata["license"] == "Apache-2.0"
    assert metadata["license-files"] == ["LICENSE"]
    assert (
        "Apache License\n                           Version 2.0" in (ROOT / "LICENSE").read_text()
    )
