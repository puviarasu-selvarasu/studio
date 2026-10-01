"""Tests for Studio's trusted AI-to-Blender execution bridge."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from kernel.adapters.blender.adapter import (
    BlenderAdapter,
    BlenderAdapterError,
)


ROOT = Path(__file__).resolve().parents[1]

AI_SHOT = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "ai_shot.py"
)


def test_ai_shot_uses_trusted_semantic_dispatch() -> None:
    source = AI_SHOT.read_text(
        encoding="utf-8"
    )

    assert "compile_animation_scene" in source
    assert "execute_animation_scene" in source

    assert "AnimatorAgent" not in source
    assert "OllamaAdapter" not in source


def test_ai_shot_has_no_dynamic_python_execution() -> None:
    source = AI_SHOT.read_text(
        encoding="utf-8"
    )

    assert "eval(" not in source
    assert "exec(" not in source
    assert "getattr(" not in source
    assert "__import__(" not in source


def test_ai_shot_uses_dynamic_eight_second_capable_timeline() -> None:
    source = AI_SHOT.read_text(
        encoding="utf-8"
    )

    assert "timeline_end_frame" in source
    assert "scene.duration_seconds" in source
    assert "PREVIEW_FPS = 12" in source
    assert "PREVIEW_FRAME_STEP = FPS // PREVIEW_FPS" in source


def test_adapter_launches_ai_shot_script(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(
        b"fake"
    )

    ir_path = tmp_path / "animation_ir.json"

    ir_path.write_text(
        "{}",
        encoding="utf-8",
    )

    output = tmp_path / "output"

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        blend_path = Path(
            command[-3]
        )

        preview_path = Path(
            command[-2]
        )

        blend_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blend_path.write_bytes(
            b"blend"
        )

        preview_path.write_bytes(
            b"png"
        )

        return Mock(
            returncode=0,
            stdout=(
                "STUDIO_AI_SHOT_OK\n"
                "STUDIO_AI_IR_EXECUTED_OK"
            ),
            stderr="",
        )

    adapter = BlenderAdapter(
        blender
    )

    with patch(
        "kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ) as run_mock:
        result = adapter.create_ai_shot(
            ir_path,
            output,
        )

    command = run_mock.call_args.args[0]

    assert "--background" in command
    assert "--factory-startup" in command

    python_index = command.index(
        "--python"
    )

    assert command[
        python_index + 1
    ].endswith(
        "ai_shot.py"
    )

    assert Path(
        command[-1]
    ) == ir_path.resolve()

    assert (
        result.blend_path
        == output.resolve()
        / "ai_shot.blend"
    )

    assert (
        result.preview_path
        == output.resolve()
        / "ai_preview.png"
    )


def test_adapter_rejects_missing_ir(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"

    blender.write_bytes(
        b"fake"
    )

    adapter = BlenderAdapter(
        blender
    )

    with pytest.raises(
        BlenderAdapterError,
        match="Animation IR file does not exist",
    ):
        adapter.create_ai_shot(
            tmp_path / "missing.json",
            tmp_path / "output",
        )


def test_adapter_requires_ai_success_marker(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"

    blender.write_bytes(
        b"fake"
    )

    ir_path = tmp_path / "animation_ir.json"

    ir_path.write_text(
        "{}",
        encoding="utf-8",
    )

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        blend_path = Path(
            command[-3]
        )

        preview_path = Path(
            command[-2]
        )

        blend_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blend_path.write_bytes(
            b"blend"
        )

        preview_path.write_bytes(
            b"png"
        )

        return Mock(
            returncode=0,
            stdout="Blender completed",
            stderr="",
        )

    adapter = BlenderAdapter(
        blender
    )

    with patch(
        "kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ):
        with pytest.raises(
            BlenderAdapterError,
            match="AI-shot success marker",
        ):
            adapter.create_ai_shot(
                ir_path,
                tmp_path / "output",
            )

def test_ai_shot_accepts_trusted_director_camera_plan() -> None:
    source = AI_SHOT.read_text(
        encoding="utf-8"
    )

    assert "load_director_camera_plan" in source
    assert "compile_camera_direction" in source
    assert "apply_camera_direction" in source

    assert (
        "STUDIO_DIRECTOR_CAMERA_EXECUTED_OK"
        in source
    )

    assert "DirectorAgent" not in source
    assert "AnimatorAgent" not in source
    assert "OllamaAdapter" not in source


def test_adapter_passes_director_camera_plan(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(
        b"fake"
    )

    ir_path = tmp_path / "animation_ir.json"
    ir_path.write_text(
        "{}",
        encoding="utf-8",
    )

    camera_path = tmp_path / "camera_plan.json"
    camera_path.write_text(
        "{}",
        encoding="utf-8",
    )

    output = tmp_path / "output"

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        blend_path = Path(
            command[-4]
        )

        preview_path = Path(
            command[-3]
        )

        assert Path(
            command[-2]
        ) == ir_path.resolve()

        assert Path(
            command[-1]
        ) == camera_path.resolve()

        blend_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blend_path.write_bytes(
            b"blend"
        )

        preview_path.write_bytes(
            b"png"
        )

        return Mock(
            returncode=0,
            stdout=(
                "STUDIO_AI_SHOT_OK\n"
                "STUDIO_AI_IR_EXECUTED_OK\n"
                "STUDIO_DIRECTOR_CAMERA_EXECUTED_OK"
            ),
            stderr="",
        )

    adapter = BlenderAdapter(
        blender
    )

    with patch(
        "kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ):
        result = adapter.create_ai_shot(
            ir_path,
            output,
            camera_plan_path=camera_path,
        )

    assert result.blend_path.is_file()
    assert result.preview_path.is_file()


def test_adapter_rejects_missing_director_camera_plan(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(
        b"fake"
    )

    ir_path = tmp_path / "animation_ir.json"
    ir_path.write_text(
        "{}",
        encoding="utf-8",
    )

    adapter = BlenderAdapter(
        blender
    )

    with pytest.raises(
        BlenderAdapterError,
        match="Director camera plan file does not exist",
    ):
        adapter.create_ai_shot(
            ir_path,
            tmp_path / "output",
            camera_plan_path=(
                tmp_path
                / "missing_camera.json"
            ),
        )


def test_adapter_requires_director_camera_execution_marker(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(
        b"fake"
    )

    ir_path = tmp_path / "animation_ir.json"
    ir_path.write_text(
        "{}",
        encoding="utf-8",
    )

    camera_path = tmp_path / "camera_plan.json"
    camera_path.write_text(
        "{}",
        encoding="utf-8",
    )

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        blend_path = Path(
            command[-4]
        )

        preview_path = Path(
            command[-3]
        )

        blend_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        blend_path.write_bytes(
            b"blend"
        )

        preview_path.write_bytes(
            b"png"
        )

        return Mock(
            returncode=0,
            stdout=(
                "STUDIO_AI_SHOT_OK\n"
                "STUDIO_AI_IR_EXECUTED_OK"
            ),
            stderr="",
        )

    adapter = BlenderAdapter(
        blender
    )

    with patch(
        "kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ):
        with pytest.raises(
            BlenderAdapterError,
            match="Director-camera execution marker",
        ):
            adapter.create_ai_shot(
                ir_path,
                tmp_path / "output",
                camera_plan_path=camera_path,
            )
