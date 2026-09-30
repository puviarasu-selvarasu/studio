"""Controlled subprocess adapter for Blender."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


class BlenderAdapterError(RuntimeError):
    """Raised when controlled Blender execution fails."""


@dataclass(frozen=True, slots=True)
class BlenderProofResult:
    """Artifacts produced by the Blender bridge proof."""

    blend_path: Path
    render_path: Path
    stdout: str


class BlenderAdapter:
    """Launch trusted Studio-owned Blender scripts."""

    def __init__(
        self,
        blender_executable: Path,
        *,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._blender_executable = blender_executable.resolve()
        self._timeout_seconds = timeout_seconds

    def create_proof_scene(
        self,
        output_directory: Path,
    ) -> BlenderProofResult:
        """Run Studio's deterministic Blender proof scene."""

        if not self._blender_executable.is_file():
            raise BlenderAdapterError(
                f"Blender executable does not exist: "
                f"{self._blender_executable}"
            )

        output_directory = output_directory.resolve()
        output_directory.mkdir(parents=True, exist_ok=True)

        blend_path = output_directory / "proof.blend"
        render_path = output_directory / "proof.png"

        script_path = Path(__file__).with_name("proof_scene.py").resolve()

        command = [
            str(self._blender_executable),
            "--background",
            "--factory-startup",
            "--python",
            str(script_path),
            "--",
            str(blend_path),
            str(render_path),
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise BlenderAdapterError(
                "Blender bridge timed out."
            ) from exc
        except OSError as exc:
            raise BlenderAdapterError(
                f"Unable to launch Blender: {exc}"
            ) from exc

        combined_output = "\n".join(
            part
            for part in (completed.stdout, completed.stderr)
            if part
        )

        if completed.returncode != 0:
            raise BlenderAdapterError(
                "Blender bridge failed with exit code "
                f"{completed.returncode}.\n{combined_output}"
            )

        if "STUDIO_BLENDER_PROOF_OK" not in combined_output:
            raise BlenderAdapterError(
                "Blender completed without Studio's success marker."
            )

        if not blend_path.is_file():
            raise BlenderAdapterError(
                f"Blender did not create scene file: {blend_path}"
            )

        if not render_path.is_file():
            raise BlenderAdapterError(
                f"Blender did not create render: {render_path}"
            )

        return BlenderProofResult(
            blend_path=blend_path,
            render_path=render_path,
            stdout=combined_output,
        )