"""Contract tests for Studio's trusted Blender pose controls."""

from __future__ import annotations

import ast
from pathlib import Path


MODULE = (
    Path(__file__).parents[1]
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "pose_controls.py"
)


def _tree() -> ast.Module:
    return ast.parse(
        MODULE.read_text(encoding="utf-8")
    )


def test_pose_controls_expose_exact_public_functions() -> None:
    functions = {
        node.name
        for node in _tree().body
        if isinstance(node, ast.FunctionDef)
    }

    assert functions == {
        "require_armature",
        "require_pose_bone",
        "set_bone_rotation_degrees",
        "insert_bone_rotation_keyframe",
    }


def test_pose_controls_use_pose_bones_and_keyframes() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "pose.bones" in source
    assert "rotation_euler" in source
    assert "keyframe_insert" in source


def test_pose_controls_do_not_execute_dynamic_python() -> None:
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


def test_pose_controls_have_no_external_execution_boundary() -> None:
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
