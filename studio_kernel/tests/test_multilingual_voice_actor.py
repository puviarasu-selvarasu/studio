import json

import pytest

from kernel.application.voice_actor_agent import (
    VoiceActorAgent,
    VoiceActorAgentError,
)


class FakeLLM:
    def __init__(
        self,
        response: str,
    ) -> None:
        self.response = response
        self.prompt = ""

    def generate(
        self,
        prompt: str,
        *,
        system_prompt=None,
        response_schema=None,
    ) -> str:
        del system_prompt
        del response_schema

        self.prompt = prompt

        return self.response


def _response(
    dialogue: str,
) -> str:
    return json.dumps(
        {
            "scene_id": "multi",
            "character_id": "momo",
            "voice_id": "studio_voice_01",
            "dialogue": dialogue,
            "emotion": "warm",
            "energy": "medium",
            "pace": "natural",
            "delivery_note": "Restrained.",
        },
        ensure_ascii=False,
    )


def test_voice_actor_receives_language_context() -> None:
    dialogue = (
        "\u96fb\u8eca\u304c\u6765\u307e\u3057\u305f\u3002"
    )

    llm = FakeLLM(
        _response(
            dialogue
        )
    )

    VoiceActorAgent(
        llm
    ).generate_plan(
        dialogue,
        scene_id="multi",
        character_id="momo",
        voice_id="studio_voice_01",
        performance_language_code="ja-JP",
    )

    assert (
        "Voice language: ja-JP"
        in llm.prompt
    )


def test_unknown_language_rejected() -> None:
    llm = FakeLLM(
        _response(
            "Hello"
        )
    )

    with pytest.raises(
        VoiceActorAgentError,
        match="Unsupported performance language",
    ):
        VoiceActorAgent(
            llm
        ).generate_plan(
            "Hello",
            scene_id="multi",
            character_id="momo",
            voice_id="studio_voice_01",
            performance_language_code="xx-XX",
        )
