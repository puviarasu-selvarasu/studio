"""Tests for the controlled Blender subprocess adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from studio_kernel.kernel.adapters.blender.adapter import (
    BlenderAdapter,
    BlenderAdapterError,
)


def test_missing_blender_executable_is_rejected(tmp_path: Path) -> None:
    adapter = BlenderAdapter(tmp_path / "missing-blender.exe")

    with pytest.raises(
        BlenderAdapterError,
        match="Blender executable does not exist",
    ):
        adapter.create_proof_scene(tmp_path / "output")


def test_proof_scene_uses_controlled_studio_script(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fake")

    output = tmp_path / "output"

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        del kwargs

        blend_path = Path(command[-2])
        render_path = Path(command[-1])

        blend_path.parent.mkdir(parents=True, exist_ok=True)
        blend_path.write_bytes(b"blend")
        render_path.write_bytes(b"png")

        return Mock(
            returncode=0,
            stdout="STUDIO_BLENDER_PROOF_OK",
            stderr="",
        )

    adapter = BlenderAdapter(blender)

    with patch(
        "studio_kernel.kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ) as run_mock:
        result = adapter.create_proof_scene(output)

    command = run_mock.call_args.args[0]

    assert "--background" in command
    assert "--factory-startup" in command
    assert "--python" in command

    python_index = command.index("--python")
    assert command[python_index + 1].endswith("proof_scene.py")
    assert command[python_index + 2] == "--"

    assert result.blend_path == output.resolve() / "proof.blend"
    assert result.render_path == output.resolve() / "proof.png"


def test_nonzero_blender_exit_is_translated(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fake")

    adapter = BlenderAdapter(blender)

    completed = Mock(
        returncode=7,
        stdout="",
        stderr="Blender failed",
    )

    with patch(
        "studio_kernel.kernel.adapters.blender.adapter.subprocess.run",
        return_value=completed,
    ):
        with pytest.raises(
            BlenderAdapterError,
            match="exit code 7",
        ):
            adapter.create_proof_scene(tmp_path / "output")


def test_blender_timeout_is_translated(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fake")

    adapter = BlenderAdapter(blender)

    with patch(
        "studio_kernel.kernel.adapters.blender.adapter.subprocess.run",
        side_effect=subprocess.TimeoutExpired(
            cmd=["blender"],
            timeout=1,
        ),
    ):
        with pytest.raises(
            BlenderAdapterError,
            match="timed out",
        ):
            adapter.create_proof_scene(tmp_path / "output")

def test_deterministic_shot_uses_controlled_studio_script(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fake")

    output = tmp_path / "output"

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        del kwargs

        blend_path = Path(command[-2])
        preview_path = Path(command[-1])

        blend_path.parent.mkdir(parents=True, exist_ok=True)
        blend_path.write_bytes(b"blend")
        preview_path.write_bytes(b"png")

        return Mock(
            returncode=0,
            stdout="STUDIO_DETERMINISTIC_SHOT_OK",
            stderr="",
        )

    adapter = BlenderAdapter(blender)

    with patch(
        "studio_kernel.kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ) as run_mock:
        result = adapter.create_deterministic_shot(output)

    command = run_mock.call_args.args[0]

    assert "--background" in command
    assert "--factory-startup" in command
    assert "--python" in command

    python_index = command.index("--python")

    assert command[python_index + 1].endswith(
        "deterministic_shot.py"
    )
    assert command[python_index + 2] == "--"

    assert result.blend_path == output.resolve() / "shot.blend"
    assert (
        result.preview_path
        == output.resolve() / "preview.png"
    )
    assert (
        "STUDIO_DETERMINISTIC_SHOT_OK"
        in result.stdout
    )


def test_deterministic_shot_rejects_missing_success_marker(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fake")

    output = tmp_path / "output"

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> Mock:
        del kwargs

        blend_path = Path(command[-2])
        preview_path = Path(command[-1])

        blend_path.parent.mkdir(parents=True, exist_ok=True)
        blend_path.write_bytes(b"blend")
        preview_path.write_bytes(b"png")

        return Mock(
            returncode=0,
            stdout="Blender finished",
            stderr="",
        )

    adapter = BlenderAdapter(blender)

    with patch(
        "studio_kernel.kernel.adapters.blender.adapter.subprocess.run",
        side_effect=fake_run,
    ):
        with pytest.raises(
            BlenderAdapterError,
            match="deterministic-shot success marker",
        ):
            adapter.create_deterministic_shot(output)


def test_deterministic_shot_requires_both_artifacts(
    tmp_path: Path,
) -> None:
    blender = tmp_path / "blender.exe"
    blender.write_bytes(b"fake")

    adapter = BlenderAdapter(blender)

    completed = Mock(
        returncode=0,
        stdout="STUDIO_DETERMINISTIC_SHOT_OK",
        stderr="",
    )

    with patch(
        "studio_kernel.kernel.adapters.blender.adapter.subprocess.run",
        return_value=completed,
    ):
        with pytest.raises(
            BlenderAdapterError,
            match="did not create shot file",
        ):
            adapter.create_deterministic_shot(
                tmp_path / "output"
            )
