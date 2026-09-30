"""Contract tests for Studio's Level-1 Blender animation actions."""

from __future__ import annotations

import ast
from pathlib import Path


MODULE = (
    Path(__file__).parents[1]
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "actions.py"
)


def _tree() -> ast.Module:
    return ast.parse(
        MODULE.read_text(encoding="utf-8")
    )


def test_actions_expose_wave_as_only_public_function() -> None:
    functions = {
        node.name
        for node in _tree().body
        if isinstance(node, ast.FunctionDef)
    }

    assert functions == {
        "idle",
        "step_forward",
        "turn_head",
        "wave",
    }


def test_wave_uses_trusted_pose_controls() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "set_bone_rotation_degrees" in source
    assert "insert_bone_rotation_keyframe" in source
    assert "upper_arm." in source
    assert "forearm." in source


def test_wave_has_bounded_input_validation() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "start_frame < 1" in source
    assert "duration_frames < 8" in source
    assert 'normalized_side not in {"L", "R"}' in source


def test_actions_do_not_execute_dynamic_python() -> None:
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


def test_actions_have_no_external_execution_boundary() -> None:
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

def test_turn_head_uses_head_bone_and_pose_controls() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert 'normalized_direction not in {"left", "right"}' in source
    assert '"head"' in source
    assert "30.0 * direction_sign" in source


def test_turn_head_has_bounded_input_validation() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "duration_frames < 6" in source
    assert "Head-turn duration must be at least 6 frames." in source

def test_idle_uses_sparse_chest_and_head_motion() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert 'armature_name,\n            "chest"' in source
    assert 'armature_name,\n            "head"' in source
    assert "(2.0, 0.0, 0.0)" in source
    assert "(-1.0, 0.0, 0.0)" in source


def test_idle_has_bounded_input_validation() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "duration_frames < 12" in source
    assert "Idle duration must be at least 12 frames." in source

def test_step_forward_uses_trusted_translation_primitives() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "get_location" in source
    assert "set_location" in source
    assert "insert_transform_keyframe" in source
    assert 'channels=("location",)' in source
    assert '"thigh.L"' in source
    assert '"thigh.R"' in source


def test_step_forward_has_bounded_input_validation() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "duration_frames < 8" in source
    assert "distance <= 0.0 or distance > 2.0" in source
    assert (
        "Step distance must be greater than 0 and at most 2."
        in source
    )


def test_actions_do_not_import_bpy_directly() -> None:
    imports = {
        alias.name.split(".")[0]
        for node in ast.walk(_tree())
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert "bpy" not in imports

def test_step_forward_preserves_existing_world_position() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "start_location = get_location(" in source
    assert "start_location[0]" in source
    assert "start_location[1] - distance" in source
    assert "start_location[2]" in source

def test_step_forward_keys_leg_pose_at_action_start() -> None:
    tree = _tree()

    step_forward = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "step_forward"
    )

    start_keyframes = [
        node
        for node in ast.walk(step_forward)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "insert_bone_rotation_keyframe"
        and len(node.args) >= 3
        and isinstance(node.args[2], ast.Name)
        and node.args[2].id == "start_frame"
    ]

    assert start_keyframes
