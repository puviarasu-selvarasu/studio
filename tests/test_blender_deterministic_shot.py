"""Contract tests for Studio's deterministic Blender shot script."""

from __future__ import annotations

import ast
from pathlib import Path


MODULE = (
    Path(__file__).parents[1]
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "deterministic_shot.py"
)


def _tree() -> ast.Module:
    return ast.parse(
        MODULE.read_text(
            encoding="utf-8"
        )
    )


def test_shot_exposes_expected_functions() -> None:
    functions = {
        node.name
        for node in _tree().body
        if isinstance(
            node,
            ast.FunctionDef,
        )
    }

    assert functions == {
        "parse_arguments",
        "clear_scene",
        "create_camera",
        "create_ground",
        "configure_render",
        "build_shot",
        "main",
    }


def test_shot_uses_existing_trusted_animation_layers() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "create_humanoid_armature" in source
    assert "configure_timeline" in source
    assert "point_camera_at" in source
    assert "set_location" in source

    assert "idle(" in source
    assert "turn_head(" in source
    assert "wave(" in source
    assert "step_forward(" in source


def test_shot_has_six_second_timeline() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "START_FRAME = 1" in source
    assert "END_FRAME = 144" in source
    assert "FPS = 24" in source


def test_shot_uses_hardware_safe_preview() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert '"BLENDER_WORKBENCH"' in source
    assert "resolution_x = 640" in source
    assert "resolution_y = 360" in source
    assert 'file_format = "PNG"' in source


def test_shot_does_not_execute_dynamic_python() -> None:
    forbidden = {
        "eval",
        "exec",
        "compile",
        "__import__",
    }

    calls = {
        node.func.id
        for node in ast.walk(
            _tree()
        )
        if isinstance(
            node,
            ast.Call,
        )
        and isinstance(
            node.func,
            ast.Name,
        )
    }

    assert calls.isdisjoint(
        forbidden
    )


def test_shot_has_no_external_execution_boundary() -> None:
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
        for node in ast.walk(
            _tree()
        )
        if isinstance(
            node,
            ast.Import,
        )
        for alias in node.names
    }

    imported_from = {
        node.module.split(".")[0]
        for node in ast.walk(
            _tree()
        )
        if isinstance(
            node,
            ast.ImportFrom,
        )
        and node.module is not None
    }

    assert (
        imports | imported_from
    ).isdisjoint(
        forbidden_roots
    )


def test_shot_emits_machine_readable_success_marker() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert (
        'print("STUDIO_DETERMINISTIC_SHOT_OK")'
        in source
    )

def test_shot_bootstraps_trusted_project_root() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert (
        "Path(__file__).resolve().parents[4]"
        in source
    )
    assert (
        "sys.path.insert(0, str(PROJECT_ROOT))"
        in source
    )
