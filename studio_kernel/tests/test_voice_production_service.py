"""Tests for trusted voice-production application service."""

from __future__ import annotations

import wave
from pathlib import Path

from kernel.application.voice_production_service import (
    VOICE_AUDIO_FILENAME,
    VOICE_PERFORMANCE_FILENAME,
    VoiceProductionService,
)
from kernel.voices import (
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformancePlan,
    voice_performance_plan_from_json,
)


class FakeTTS:
    """Write a deterministic local test WAV."""

    def __init__(
        self,
    ) -> None:
        self.calls: list[
            tuple[
                str,
                Path,
            ]
        ] = []

    def synthesize(
        self,
        text: str,
        output_path: Path,
    ) -> Path:
        self.calls.append(
            (
                text,
                output_path,
            )
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with wave.open(
            str(
                output_path
            ),
            "wb",
        ) as wav:
            wav.setnchannels(
                1
            )

            wav.setsampwidth(
                2
            )

            wav.setframerate(
                16000
            )

            wav.writeframes(
                b"\x00\x00"
                * 1600
            )

        return output_path


def _plan() -> VoicePerformancePlan:
    return VoicePerformancePlan(
        scene_id="scene_voice_01",
        character_id="momo",
        voice_id="studio_voice_01",
        dialogue="The train is finally here.",
        emotion=VoiceEmotion.WARM,
        energy=VoiceEnergy.MEDIUM,
        pace=VoicePace.NATURAL,
        delivery_note="Quiet relief.",
    )


def test_voice_production_writes_wav_and_plan_manifest(
    tmp_path: Path,
) -> None:
    tts = FakeTTS()

    result = VoiceProductionService(
        tts
    ).render(
        _plan(),
        tmp_path,
    )

    assert result.audio_path == (
        tmp_path
        / VOICE_AUDIO_FILENAME
    )

    assert (
        result.performance_path
        == tmp_path
        / VOICE_PERFORMANCE_FILENAME
    )

    assert result.audio_path.is_file()

    assert (
        result.performance_path
        .is_file()
    )

    loaded = (
        voice_performance_plan_from_json(
            result.performance_path.read_text(
                encoding="utf-8"
            )
        )
    )

    assert loaded == _plan()


def test_voice_production_sends_only_authored_dialogue_to_tts(
    tmp_path: Path,
) -> None:
    tts = FakeTTS()

    VoiceProductionService(
        tts
    ).render(
        _plan(),
        tmp_path,
    )

    assert tts.calls == [
        (
            "The train is finally here.",
            tmp_path
            / VOICE_AUDIO_FILENAME,
        )
    ]
