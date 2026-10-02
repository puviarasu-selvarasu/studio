"""Tests for Studio's AI Voice Actor Agent."""

from __future__ import annotations

import json

import pytest

from kernel.application.voice_actor_agent import (
    VoiceActorAgent,
    VoiceActorAgentError,
)
from kernel.voices import (
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
)


class FakeLLM:
    """Deterministic structured-output LLM test double."""

    def __init__(
        self,
        response: str,
        *,
        error: Exception | None = None,
    ) -> None:
        self.response = response
        self.error = error
        self.calls: list[
            tuple[
                str,
                str | None,
                dict[str, object] | None,
            ]
        ] = []

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        response_schema: dict[str, object] | None = None,
    ) -> str:
        self.calls.append(
            (
                prompt,
                system_prompt,
                response_schema,
            )
        )

        if self.error is not None:
            raise self.error

        return self.response


def _response(
    **changes: object,
) -> str:
    data: dict[str, object] = {
        "scene_id": "scene_voice_01",
        "character_id": "momo",
        "voice_id": "studio_voice_01",
        "dialogue": "The train is finally here.",
        "emotion": "warm",
        "energy": "medium",
        "pace": "natural",
        "delivery_note": (
            "Quiet relief with restrained warmth."
        ),
    }

    data.update(
        changes
    )

    return json.dumps(
        data
    )


def test_voice_actor_generates_trusted_performance_plan() -> None:
    llm = FakeLLM(
        _response()
    )

    plan = VoiceActorAgent(
        llm
    ).generate_plan(
        "The train is finally here.",
        scene_id="scene_voice_01",
        character_id="momo",
        voice_id="studio_voice_01",
        direction=(
            "She has been waiting alone for a long time."
        ),
    )

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

    assert plan.dialogue == (
        "The train is finally here."
    )


def test_voice_actor_prompt_forbids_dialogue_rewrite_and_engine_commands() -> None:
    llm = FakeLLM(
        _response()
    )

    VoiceActorAgent(
        llm
    ).generate_plan(
        "The train is finally here.",
        scene_id="scene_voice_01",
        character_id="momo",
        voice_id="studio_voice_01",
    )

    prompt = llm.calls[0][0]
    system = llm.calls[0][1]
    schema = llm.calls[0][2]

    assert (
        "Preserve dialogue exactly."
        in prompt
    )

    assert (
        "Do not add spoken words."
        in prompt
    )

    assert (
        "Never emit shell commands."
        in system
    )

    assert schema is not None


def test_voice_actor_rejects_changed_character_identity() -> None:
    llm = FakeLLM(
        _response(
            character_id="someone_else"
        )
    )

    with pytest.raises(
        VoiceActorAgentError,
        match="character ID",
    ):
        VoiceActorAgent(
            llm
        ).generate_plan(
            "The train is finally here.",
            scene_id="scene_voice_01",
            character_id="momo",
            voice_id="studio_voice_01",
        )


def test_voice_actor_rejects_rewritten_dialogue() -> None:
    llm = FakeLLM(
        _response(
            dialogue="The train has arrived!"
        )
    )

    with pytest.raises(
        VoiceActorAgentError,
        match="authored dialogue",
    ):
        VoiceActorAgent(
            llm
        ).generate_plan(
            "The train is finally here.",
            scene_id="scene_voice_01",
            character_id="momo",
            voice_id="studio_voice_01",
        )


def test_voice_actor_rejects_unknown_voice_before_llm() -> None:
    llm = FakeLLM(
        _response()
    )

    with pytest.raises(
        VoiceActorAgentError,
        match="Unknown voice identity",
    ):
        VoiceActorAgent(
            llm
        ).generate_plan(
            "Hello.",
            scene_id="scene_voice_01",
            character_id="momo",
            voice_id="missing_voice",
        )

    assert llm.calls == []


def test_voice_actor_translates_invalid_json() -> None:
    llm = FakeLLM(
        "not-json"
    )

    with pytest.raises(
        VoiceActorAgentError,
        match="invalid performance JSON",
    ):
        VoiceActorAgent(
            llm
        ).generate_plan(
            "The train is finally here.",
            scene_id="scene_voice_01",
            character_id="momo",
            voice_id="studio_voice_01",
        )


def test_voice_actor_translates_llm_failure() -> None:
    llm = FakeLLM(
        "",
        error=RuntimeError(
            "local model unavailable"
        ),
    )

    with pytest.raises(
        VoiceActorAgentError,
        match="LLM generation failed",
    ):
        VoiceActorAgent(
            llm
        ).generate_plan(
            "The train is finally here.",
            scene_id="scene_voice_01",
            character_id="momo",
            voice_id="studio_voice_01",
        )
