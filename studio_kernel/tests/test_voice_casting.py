"""Tests for multi-character Studio voice casting."""

from __future__ import annotations

import json
import wave
from pathlib import Path

import pytest

from kernel.application.voice_actor_agent import (
    VoiceActorAgent,
)
from kernel.application.voice_casting_service import (
    MultiVoiceProductionService,
    VoiceCastingService,
    VoiceCastingServiceError,
    VoiceTTSRegistry,
)
from kernel.voices import (
    STUDIO_VOICE_01,
    STUDIO_VOICE_02,
    CharacterVoiceAssignment,
    VoiceCast,
    VoiceCastError,
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformancePlan,
)


def _cast() -> VoiceCast:
    return VoiceCast(
        assignments=(
            CharacterVoiceAssignment(
                character_id="momo",
                voice_id="studio_voice_01",
            ),
            CharacterVoiceAssignment(
                character_id="rival_demo",
                voice_id="studio_voice_02",
            ),
        )
    )


class CharacterAwareFakeLLM:
    """One fake LLM serving multiple cast characters."""

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        response_schema: dict[str, object] | None = None,
    ) -> str:
        del system_prompt
        del response_schema

        if (
            "Character ID: momo"
            in prompt
        ):
            return json.dumps(
                {
                    "scene_id": "scene_dialogue_01",
                    "character_id": "momo",
                    "voice_id": "studio_voice_01",
                    "dialogue": "We should leave now.",
                    "emotion": "warm",
                    "energy": "medium",
                    "pace": "natural",
                    "delivery_note": "Quiet urgency.",
                }
            )

        if (
            "Character ID: rival_demo"
            in prompt
        ):
            return json.dumps(
                {
                    "scene_id": "scene_dialogue_01",
                    "character_id": "rival_demo",
                    "voice_id": "studio_voice_02",
                    "dialogue": "You are already too late.",
                    "emotion": "serious",
                    "energy": "low",
                    "pace": "slow",
                    "delivery_note": "Controlled and firm.",
                }
            )

        raise AssertionError(
            "Unexpected character prompt."
        )


class FakeTTS:
    """Generate deterministic WAVs while recording routing."""

    def __init__(
        self,
        marker: int,
    ) -> None:
        self.marker = marker
        self.calls: list[str] = []

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

        sample = (
            int(
                self.marker
            )
            .to_bytes(
                2,
                byteorder="little",
                signed=True,
            )
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
                sample
                * 1600
            )

        return output_path


def test_voice_catalog_contains_two_distinct_semantic_voices() -> None:
    assert (
        STUDIO_VOICE_01.voice_id
        == "studio_voice_01"
    )

    assert (
        STUDIO_VOICE_02.voice_id
        == "studio_voice_02"
    )

    assert (
        STUDIO_VOICE_01
        != STUDIO_VOICE_02
    )


def test_voice_cast_rejects_duplicate_character_assignment() -> None:
    with pytest.raises(
        VoiceCastError,
        match="only one",
    ):
        VoiceCast(
            assignments=(
                CharacterVoiceAssignment(
                    character_id="momo",
                    voice_id="studio_voice_01",
                ),
                CharacterVoiceAssignment(
                    character_id="momo",
                    voice_id="studio_voice_02",
                ),
            )
        )


def test_same_voice_actor_agent_plans_multiple_characters() -> None:
    casting = VoiceCastingService(
        _cast()
    )

    agent = VoiceActorAgent(
        CharacterAwareFakeLLM()
    )

    momo = casting.plan_line(
        agent,
        "We should leave now.",
        scene_id="scene_dialogue_01",
        character_id="momo",
        direction="Concerned but composed.",
    )

    rival = casting.plan_line(
        agent,
        "You are already too late.",
        scene_id="scene_dialogue_01",
        character_id="rival_demo",
        direction="Cold and controlled.",
    )

    assert (
        momo.voice_id
        == "studio_voice_01"
    )

    assert (
        rival.voice_id
        == "studio_voice_02"
    )

    assert (
        momo.emotion
        is VoiceEmotion.WARM
    )

    assert (
        rival.emotion
        is VoiceEmotion.SERIOUS
    )


def test_casting_rejects_unknown_semantic_voice() -> None:
    cast = VoiceCast(
        assignments=(
            CharacterVoiceAssignment(
                character_id="momo",
                voice_id="missing_voice",
            ),
        )
    )

    with pytest.raises(
        VoiceCastingServiceError,
        match="unknown voice identity",
    ):
        VoiceCastingService(
            cast
        )


def test_multi_voice_production_routes_each_character_to_its_voice(
    tmp_path: Path,
) -> None:
    voice_01 = FakeTTS(
        100
    )

    voice_02 = FakeTTS(
        200
    )

    casting = VoiceCastingService(
        _cast()
    )

    registry = VoiceTTSRegistry(
        {
            "studio_voice_01": voice_01,
            "studio_voice_02": voice_02,
        }
    )

    production = (
        MultiVoiceProductionService(
            casting,
            registry,
        )
    )

    momo = VoicePerformancePlan(
        scene_id="scene_dialogue_01",
        character_id="momo",
        voice_id="studio_voice_01",
        dialogue="We should leave now.",
        emotion=VoiceEmotion.WARM,
        energy=VoiceEnergy.MEDIUM,
        pace=VoicePace.NATURAL,
    )

    rival = VoicePerformancePlan(
        scene_id="scene_dialogue_01",
        character_id="rival_demo",
        voice_id="studio_voice_02",
        dialogue="You are already too late.",
        emotion=VoiceEmotion.SERIOUS,
        energy=VoiceEnergy.LOW,
        pace=VoicePace.SLOW,
    )

    production.render(
        momo,
        tmp_path
        / "momo",
    )

    production.render(
        rival,
        tmp_path
        / "rival",
    )

    assert voice_01.calls == [
        "We should leave now."
    ]

    assert voice_02.calls == [
        "You are already too late."
    ]


def test_multi_voice_production_rejects_character_voice_drift(
    tmp_path: Path,
) -> None:
    casting = VoiceCastingService(
        _cast()
    )

    registry = VoiceTTSRegistry(
        {
            "studio_voice_01": FakeTTS(
                100
            ),
            "studio_voice_02": FakeTTS(
                200
            ),
        }
    )

    production = (
        MultiVoiceProductionService(
            casting,
            registry,
        )
    )

    wrong = VoicePerformancePlan(
        scene_id="scene_dialogue_01",
        character_id="momo",
        voice_id="studio_voice_02",
        dialogue="This should not render.",
        emotion=VoiceEmotion.NEUTRAL,
        energy=VoiceEnergy.MEDIUM,
        pace=VoicePace.NATURAL,
    )

    with pytest.raises(
        VoiceCastingServiceError,
        match="persistent voice cast",
    ):
        production.render(
            wrong,
            tmp_path,
        )
