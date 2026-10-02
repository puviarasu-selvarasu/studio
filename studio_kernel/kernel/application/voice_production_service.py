"""Trusted application service for voice-production artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kernel.ports.tts import (
    TTSPort,
)
from kernel.voices import (
    VoicePerformancePlan,
    voice_performance_plan_to_json,
)


VOICE_PERFORMANCE_FILENAME = (
    "voice_performance.json"
)

VOICE_AUDIO_FILENAME = (
    "dialogue.wav"
)


class VoiceProductionError(
    RuntimeError
):
    """Raised when trusted voice production fails."""


@dataclass(
    frozen=True,
    slots=True,
)
class VoiceProductionResult:
    """Artifacts produced for one spoken line."""

    performance_path: Path
    audio_path: Path


class VoiceProductionService:
    """Persist performance intent and execute speech through TTSPort."""

    def __init__(
        self,
        tts: TTSPort,
    ) -> None:
        self._tts = tts

    def render(
        self,
        plan: VoicePerformancePlan,
        output_directory: Path,
    ) -> VoiceProductionResult:
        """Render one validated performance plan to local WAV."""

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        audio_path = (
            output_directory
            / VOICE_AUDIO_FILENAME
        )

        performance_path = (
            output_directory
            / VOICE_PERFORMANCE_FILENAME
        )

        try:
            returned = (
                self._tts.synthesize(
                    plan.dialogue,
                    audio_path,
                )
            )
        except Exception as exc:
            raise VoiceProductionError(
                "TTS synthesis failed."
            ) from exc

        if (
            Path(
                returned
            ).resolve()
            != audio_path.resolve()
        ):
            raise VoiceProductionError(
                "TTS returned an unexpected output path."
            )

        if (
            not audio_path.is_file()
            or audio_path.stat().st_size <= 0
        ):
            raise VoiceProductionError(
                "TTS did not produce a non-empty audio file."
            )

        performance_path.write_text(
            voice_performance_plan_to_json(
                plan
            ),
            encoding="utf-8",
            newline="\n",
        )

        return VoiceProductionResult(
            performance_path=(
                performance_path
            ),
            audio_path=audio_path,
        )
