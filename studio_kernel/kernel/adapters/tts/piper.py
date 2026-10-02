"""Trusted local Piper implementation of Studio's TTSPort."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


class PiperTTSError(
    RuntimeError
):
    """Raised when local Piper synthesis fails."""


class PiperTTSAdapter:
    """Run a trusted Piper executable and trusted local voice model."""

    def __init__(
        self,
        executable_path: Path,
        model_path: Path,
        *,
        config_path: Path | None = None,
        speaker_id: int | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._executable_path = Path(
            executable_path
        )

        self._model_path = Path(
            model_path
        )

        self._config_path = (
            Path(
                config_path
            )
            if config_path is not None
            else None
        )

        if (
            speaker_id is not None
            and (
                not isinstance(
                    speaker_id,
                    int,
                )
                or speaker_id < 0
            )
        ):
            raise ValueError(
                "speaker_id must be a non-negative integer or None."
            )

        self._speaker_id = (
            speaker_id
        )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero."
            )

        self._timeout_seconds = float(
            timeout_seconds
        )

    def synthesize(
        self,
        text: str,
        output_path: Path,
    ) -> Path:
        """Generate one WAV without shell execution."""

        normalized = text.strip()

        if not normalized:
            raise ValueError(
                "TTS text must not be blank."
            )

        output_path = Path(
            output_path
        )

        if (
            output_path.suffix.lower()
            != ".wav"
        ):
            raise ValueError(
                "Piper output must be a .wav file."
            )

        if not self._executable_path.is_file():
            raise PiperTTSError(
                "Piper executable does not exist: "
                + str(
                    self._executable_path
                )
            )

        if not self._model_path.is_file():
            raise PiperTTSError(
                "Piper voice model does not exist: "
                + str(
                    self._model_path
                )
            )

        if (
            self._config_path is not None
            and not self._config_path.is_file()
        ):
            raise PiperTTSError(
                "Piper config does not exist: "
                + str(
                    self._config_path
                )
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            str(
                self._executable_path
            ),
            "--model",
            str(
                self._model_path
            ),
            "--output_file",
            str(
                output_path
            ),
        ]

        if (
            self._config_path
            is not None
        ):
            command.extend(
                [
                    "--config",
                    str(
                        self._config_path
                    ),
                ]
            )

        if (
            self._speaker_id
            is not None
        ):
            command.extend(
                [
                    "--speaker",
                    str(
                        self._speaker_id
                    ),
                ]
            )

        try:
            result = subprocess.run(
                command,
                input=(
                    normalized
                    + "\n"
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={
                    **os.environ,
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONUTF8": "1",
                },
                timeout=(
                    self._timeout_seconds
                ),
                check=False,
                shell=False,
            )
        except (
            OSError,
            subprocess.TimeoutExpired,
        ) as exc:
            raise PiperTTSError(
                "Unable to execute local Piper."
            ) from exc

        if result.returncode != 0:
            message = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Piper exited unsuccessfully."
            )

            raise PiperTTSError(
                message
            )

        if (
            not output_path.is_file()
            or output_path.stat().st_size <= 0
        ):
            raise PiperTTSError(
                "Piper did not create a non-empty WAV."
            )

        header = (
            output_path.read_bytes()[
                :4
            ]
        )

        if header != b"RIFF":
            raise PiperTTSError(
                "Piper output is not a RIFF WAV file."
            )

        return output_path
