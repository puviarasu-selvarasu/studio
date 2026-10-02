"""Strict deterministic JSON for voice-performance plans."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from kernel.voices.models import (
    VoiceDomainError,
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformancePlan,
)


VOICE_PERFORMANCE_SCHEMA_VERSION = 1


class VoicePerformanceParseError(
    VoiceDomainError
):
    """Raised when untrusted voice-plan JSON is invalid."""


_PLAN_KEYS = {
    "scene_id",
    "character_id",
    "voice_id",
    "dialogue",
    "emotion",
    "energy",
    "pace",
    "delivery_note",
}


def voice_performance_plan_to_data(
    plan: VoicePerformancePlan,
) -> dict[str, object]:
    """Convert a trusted plan to deterministic plain data."""

    return {
        "scene_id": plan.scene_id,
        "character_id": plan.character_id,
        "voice_id": plan.voice_id,
        "dialogue": plan.dialogue,
        "emotion": plan.emotion.value,
        "energy": plan.energy.value,
        "pace": plan.pace.value,
        "delivery_note": (
            plan.delivery_note
        ),
    }


def voice_performance_plan_to_json(
    plan: VoicePerformancePlan,
) -> str:
    """Serialize a trusted plan."""

    document = {
        "schema_version": (
            VOICE_PERFORMANCE_SCHEMA_VERSION
        ),
        "performance": (
            voice_performance_plan_to_data(
                plan
            )
        ),
    }

    return (
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def voice_performance_plan_from_data(
    data: Mapping[str, Any],
) -> VoicePerformancePlan:
    """Parse one strict performance mapping."""

    actual = set(
        data.keys()
    )

    if actual != _PLAN_KEYS:
        missing = sorted(
            _PLAN_KEYS
            - actual
        )

        extra = sorted(
            actual
            - _PLAN_KEYS
        )

        raise VoicePerformanceParseError(
            "Voice performance keys mismatch. "
            + "missing="
            + repr(missing)
            + " extra="
            + repr(extra)
        )

    try:
        return VoicePerformancePlan(
            scene_id=str(
                data["scene_id"]
            ),
            character_id=str(
                data["character_id"]
            ),
            voice_id=str(
                data["voice_id"]
            ),
            dialogue=str(
                data["dialogue"]
            ),
            emotion=VoiceEmotion(
                data["emotion"]
            ),
            energy=VoiceEnergy(
                data["energy"]
            ),
            pace=VoicePace(
                data["pace"]
            ),
            delivery_note=str(
                data["delivery_note"]
            ),
        )
    except (
        ValueError,
        TypeError,
        VoiceDomainError,
    ) as exc:
        raise VoicePerformanceParseError(
            "Invalid voice performance data."
        ) from exc


def voice_performance_plan_from_json(
    raw: str,
) -> VoicePerformancePlan:
    """Parse strict Voice Actor Agent JSON."""

    try:
        data = json.loads(
            raw
        )
    except json.JSONDecodeError as exc:
        raise VoicePerformanceParseError(
            "Voice performance is not valid JSON."
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise VoicePerformanceParseError(
            "Voice performance JSON must be an object."
        )

    # Agent responses contain the performance object directly.
    if (
        "schema_version"
        not in data
    ):
        return voice_performance_plan_from_data(
            data
        )

    if set(
        data.keys()
    ) != {
        "schema_version",
        "performance",
    }:
        raise VoicePerformanceParseError(
            "Voice manifest keys are invalid."
        )

    if (
        data["schema_version"]
        != VOICE_PERFORMANCE_SCHEMA_VERSION
    ):
        raise VoicePerformanceParseError(
            "Unsupported voice-performance schema version."
        )

    performance = data[
        "performance"
    ]

    if not isinstance(
        performance,
        dict,
    ):
        raise VoicePerformanceParseError(
            "Voice manifest performance must be an object."
        )

    return voice_performance_plan_from_data(
        performance
    )
