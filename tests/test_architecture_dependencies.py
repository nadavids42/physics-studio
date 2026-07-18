"""Semantic dependency rules and a reproducible import-cycle check."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "physics_playground"


def module_name(path: Path) -> str:
    parts = path.relative_to(ROOT).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def imported_modules(path: Path) -> set[str]:
    owner = module_name(path).split(".")
    imports: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = owner[: -node.level]
                target = ".".join((*base, *(node.module or "").split("."))).rstrip(".")
            else:
                target = node.module or ""
            if target:
                imports.add(target)
    return imports


def test_prohibited_dependencies() -> None:
    violations: list[str] = []
    for path in PACKAGE.rglob("*.py"):
        owner = module_name(path)
        imports = imported_modules(path)
        forbidden: tuple[str, ...] = ()
        if owner.endswith(".physics"):
            forbidden = (
                "streamlit",
                "matplotlib",
                "physics_playground.presentation",
                "physics_playground.canvas",
                "physics_playground.education",
                "physics_playground.missions",
                "physics_playground.notebook",
                "physics_playground.profiles",
            )
        elif owner == "physics_playground.simulation_plugin" or owner.endswith(".plugin"):
            forbidden = (
                "streamlit",
                "physics_playground.presentation",
                "physics_playground.registry",
                "physics_playground.education",
            )
        elif owner == "physics_playground.registry":
            forbidden = ("physics_playground.education", "physics_playground.presentation")
        elif owner in {
            "physics_playground.education.models",
            "physics_playground.education.validation",
        }:
            forbidden = (
                "streamlit",
                "physics_playground.presentation",
                "physics_playground.registry",
                "physics_playground.subjects",
                "physics_playground.profiles",
            )
        for dependency in imports:
            if any(dependency == item or dependency.startswith(f"{item}.") for item in forbidden):
                violations.append(f"{owner} -> {dependency}")
    assert not violations, "Prohibited dependencies:\n" + "\n".join(sorted(violations))


def test_internal_import_graph_is_acyclic() -> None:
    """Detect Python-package cycles with the same AST graph on every platform."""

    modules = {module_name(path): path for path in PACKAGE.rglob("*.py")}
    graph: dict[str, set[str]] = defaultdict(set)
    for owner, path in modules.items():
        for dependency in imported_modules(path):
            candidate = dependency
            while candidate and candidate not in modules:
                candidate = candidate.rpartition(".")[0]
            if candidate and candidate != owner:
                graph[owner].add(candidate)

    active: list[str] = []
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            cycle = active[active.index(node) :] + [node]
            raise AssertionError("Import cycle: " + " -> ".join(cycle))
        if node in visited:
            return
        active.append(node)
        for dependency in sorted(graph[node]):
            visit(dependency)
        active.pop()
        visited.add(node)

    for module in sorted(modules):
        visit(module)
