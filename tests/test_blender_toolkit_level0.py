"""Contract tests for Blender Toolkit Level 0."""

from __future__ import annotations

import ast
from pathlib import Path


TOOLKIT = (
    Path(__file__).parents[1]
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "toolkit_level0.py"
)


def _tree() -> ast.Module:
    return ast.parse(
        TOOLKIT.read_text(encoding="utf-8")
    )


def _functions() -> set[str]:
    return {
        node.name
        for node in _tree().body
        if isinstance(node, ast.FunctionDef)
    }


def test_level0_exposes_only_expected_public_primitives() -> None:
    expected = {
        "require_object",
        "set_location",
        "set_rotation_degrees",
        "set_scale",
        "insert_transform_keyframe",
        "configure_timeline",
        "point_camera_at",
    }

    assert _functions() == expected


def test_level0_does_not_execute_dynamic_python() -> None:
    forbidden_calls = {
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

    assert calls.isdisjoint(forbidden_calls)


def test_level0_has_no_subprocess_boundary() -> None:
    imports = {
        alias.name
        for node in ast.walk(_tree())
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    imported_from = {
        node.module
        for node in ast.walk(_tree())
        if isinstance(node, ast.ImportFrom)
        and node.module is not None
    }

    assert "subprocess" not in imports
    assert "subprocess" not in imported_from


def test_level0_has_no_llm_or_network_dependency() -> None:
    forbidden_roots = {
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