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
        "parent_object_to_bone",
        "create_debug_segment",
        "create_debug_head",
        "create_debug_body",
        "render_preview_frames",
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


def test_shot_uses_half_rate_engineering_preview() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "PREVIEW_FPS = 12" in source
    assert (
        "PREVIEW_FRAME_STEP = FPS // PREVIEW_FPS"
        in source
    )


def test_shot_renders_numbered_preview_frames() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "def render_preview_frames(" in source
    assert "PREVIEW_FRAME_STEP" in source
    assert 'f"frame_{rendered_count:04d}.png"' in source
    assert "STUDIO_PREVIEW_FRAMES_OK" in source
    assert "STUDIO_PREVIEW_FRAME_COUNT=" in source
    assert "STUDIO_PREVIEW_FPS=" in source

def test_shot_creates_visible_bone_parented_debug_body() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "def parent_object_to_bone(" in source
    assert 'obj.parent_type = "BONE"' in source
    assert "obj.parent_bone = bone_name" in source

    assert "def create_debug_segment(" in source
    assert "primitive_cube_add(" in source

    assert "def create_debug_head(" in source
    assert "primitive_uv_sphere_add(" in source

    assert "def create_debug_body(" in source
    assert "rig = create_humanoid_armature(" in source
    assert "create_debug_body(rig)" in source

    for bone_name in (
        "pelvis",
        "spine",
        "chest",
        "neck",
        "upper_arm.L",
        "forearm.L",
        "hand.L",
        "upper_arm.R",
        "forearm.R",
        "hand.R",
        "thigh.L",
        "shin.L",
        "foot.L",
        "thigh.R",
        "shin.R",
        "foot.R",
    ):
        assert f'("{bone_name}",' in source

def test_debug_body_preserves_world_transform() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "world_matrix = obj.matrix_world.copy()" in source
    assert "obj.matrix_world = world_matrix" in source

    assert "matrix_parent_inverse" not in source

    assert (
        source.count(
            "bpy.context.view_layer.update()"
        )
        >= 4
    )
