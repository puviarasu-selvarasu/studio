import json
import wave
from pathlib import Path

import pytest

from kernel.application.multilingual_voice_service import (
    MultilingualVoiceError,
    MultilingualVoiceProductionService,
    MultilingualVoiceTTSRegistry,
)
from kernel.voices import (
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformancePlan,
)


class FakeTTS:
    def __init__(
        self,
    ) -> None:
        self.calls = []

    def synthesize(
        self,
        text: str,
        output_path: Path,
    ) -> Path:
        self.calls.append(
            text
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with wave.open(
            str(output_path),
            "wb",
        ) as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(
                b"\x01\x00"
                * 1600
            )

        return output_path


def _plan(
    text: str,
) -> VoicePerformancePlan:
    return VoicePerformancePlan(
        scene_id="multi",
        character_id="momo",
        voice_id="studio_voice_01",
        dialogue=text,
        emotion=VoiceEmotion.WARM,
        energy=VoiceEnergy.MEDIUM,
        pace=VoicePace.NATURAL,
    )


def test_tamil_routes_to_tamil_tts(
    tmp_path: Path,
) -> None:
    adapter = FakeTTS()

    service = (
        MultilingualVoiceProductionService(
            MultilingualVoiceTTSRegistry(
                {
                    "studio_voice_01_ta": (
                        adapter
                    )
                }
            )
        )
    )

    text = (
        "\u0bb5\u0ba3\u0b95\u0bcd\u0b95\u0bae\u0bcd"
    )

    result = service.render(
        _plan(
            text
        ),
        "ta-IN",
        tmp_path,
    )

    assert adapter.calls == [
        text
    ]

    context = json.loads(
        result.language_context_path
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        context[
            "language_code"
        ]
        == "ta-IN"
    )


def test_language_not_added_to_voice_plan() -> None:
    assert not hasattr(
        _plan(
            "Hello"
        ),
        "language_code",
    )


def test_unknown_language_rejected(
    tmp_path: Path,
) -> None:
    service = (
        MultilingualVoiceProductionService(
            MultilingualVoiceTTSRegistry(
                {
                    "studio_voice_01_en": (
                        FakeTTS()
                    )
                }
            )
        )
    )

    with pytest.raises(
        MultilingualVoiceError
    ):
        service.render(
            _plan(
                "Hello"
            ),
            "xx-XX",
            tmp_path,
        )
