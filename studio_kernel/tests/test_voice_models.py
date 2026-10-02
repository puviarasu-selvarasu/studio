"""Tests for Studio voice-performance domain."""

from __future__ import annotations

import json

import pytest

from kernel.voices import (
    STUDIO_VOICE_01,
    VoiceDomainError,
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformanceParseError,
    VoicePerformancePlan,
    get_voice_identity,
    voice_performance_plan_from_json,
    voice_performance_plan_to_json,
)


def _plan() -> VoicePerformancePlan:
    return VoicePerformancePlan(
        scene_id="scene_voice_01",
        character_id="momo",
        voice_id="studio_voice_01",
        dialogue="The train is finally here.",
        emotion=VoiceEmotion.WARM,
        energy=VoiceEnergy.MEDIUM,
        pace=VoicePace.NATURAL,
        delivery_note=(
            "Relieved, but keep the delivery restrained."
        ),
    )


def test_voice_identity_is_separate_from_character_identity() -> None:
    assert STUDIO_VOICE_01.voice_id == (
        "studio_voice_01"
    )

    assert (
        STUDIO_VOICE_01.voice_id
        != "momo"
    )

    assert get_voice_identity(
        "studio_voice_01"
    ) == STUDIO_VOICE_01


def test_voice_performance_plan_is_bounded() -> None:
    plan = _plan()

    assert (
        plan.emotion
        is VoiceEmotion.WARM
    )

    assert (
        plan.energy
        is VoiceEnergy.MEDIUM
    )

    assert (
        plan.pace
        is VoicePace.NATURAL
    )


def test_voice_plan_round_trips_through_manifest_json() -> None:
    plan = _plan()

    loaded = (
        voice_performance_plan_from_json(
            voice_performance_plan_to_json(
                plan
            )
        )
    )

    assert loaded == plan


def test_voice_plan_rejects_blank_dialogue() -> None:
    with pytest.raises(
        VoiceDomainError
    ):
        VoicePerformancePlan(
            scene_id="scene_voice_01",
            character_id="momo",
            voice_id="studio_voice_01",
            dialogue="   ",
            emotion=VoiceEmotion.NEUTRAL,
            energy=VoiceEnergy.MEDIUM,
            pace=VoicePace.NATURAL,
        )


def test_voice_parser_rejects_unknown_emotion() -> None:
    data = {
        "scene_id": "scene_voice_01",
        "character_id": "momo",
        "voice_id": "studio_voice_01",
        "dialogue": "Hello.",
        "emotion": "melodramatic_super_mode",
        "energy": "medium",
        "pace": "natural",
        "delivery_note": "",
    }

    with pytest.raises(
        VoicePerformanceParseError
    ):
        voice_performance_plan_from_json(
            json.dumps(
                data
            )
        )


def test_voice_parser_rejects_extra_engine_control() -> None:
    data = {
        "scene_id": "scene_voice_01",
        "character_id": "momo",
        "voice_id": "studio_voice_01",
        "dialogue": "Hello.",
        "emotion": "neutral",
        "energy": "medium",
        "pace": "natural",
        "delivery_note": "",
        "shell_command": "anything",
    }

    with pytest.raises(
        VoicePerformanceParseError
    ):
        voice_performance_plan_from_json(
            json.dumps(
                data
            )
        )
