"""Contract tests for Studio's Blender humanoid rig builder."""

from __future__ import annotations

import ast
from pathlib import Path


MODULE = (
    Path(__file__).parents[1]
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "humanoid_rig.py"
)


def _tree() -> ast.Module:
    return ast.parse(
        MODULE.read_text(encoding="utf-8")
    )


def test_rig_builder_exposes_expected_function() -> None:
    functions = {
        node.name
        for node in _tree().body
        if isinstance(node, ast.FunctionDef)
    }

    assert functions == {
        "create_humanoid_armature",
    }


def test_rig_builder_uses_canonical_contract() -> None:
    source = MODULE.read_text(encoding="utf-8")

    assert "HUMANOID_RIG" in source
    assert "edit_bones.new" in source


def test_rig_builder_does_not_execute_dynamic_python() -> None:
    forbidden = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    calls = {
        node.func.id
        for node in ast.walk(_tree())
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
    }

    assert calls.isdisjoint(forbidden)


def test_rig_builder_has_no_external_execution_boundary() -> None:
    forbidden_roots = {
        "subprocess",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "ollama",
        "openai",
    }

    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(_tree())
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    imported_from = {
        node.module.split(".")[0]
        for node in ast.walk(_tree())
        if isinstance(node, ast.ImportFrom)
        and node.module is not None
    }

    assert (imports | imported_from).isdisjoint(
        forbidden_roots
    )
