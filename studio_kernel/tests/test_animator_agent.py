"""Tests for Studio AI Animator Agent."""

from __future__ import annotations

import json

import pytest

from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.application.animator_agent import (
    AnimatorAgent,
    AnimatorAgentError,
)
from kernel.capabilities.models import (
    CapabilityRegistry,
    CharacterCapability,
)


class FakeLLM:
    """Minimal deterministic LLM test double."""

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


def _registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        characters=(
            CharacterCapability(
                character_id="momo",
                actions=(
                    "idle",
                    "turn_head",
                    "wave",
                    "step_forward",
                ),
            ),
        )
    )


def _valid_response() -> str:
    return json.dumps(
        {
            "scene_id": "scene_ai_1",
            "duration_seconds": 8.0,
            "character_id": "momo",
            "actions": [
                {
                    "action": "idle",
                    "start_seconds": 0.0,
                    "duration_seconds": 2.0,
                },
                {
                    "action": "turn_head",
                    "start_seconds": 2.0,
                    "duration_seconds": 1.0,
                },
                {
                    "action": "wave",
                    "start_seconds": 3.0,
                    "duration_seconds": 3.0,
                },
                {
                    "action": "step_forward",
                    "start_seconds": 6.0,
                    "duration_seconds": 2.0,
                },
            ],
        }
    )


def test_agent_generates_trusted_animation_scene() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = AnimatorAgent(
        llm,
        _registry(),
    )

    scene = agent.generate_scene(
        (
            "Momo notices someone, turns her head, "
            "waves, then steps forward."
        ),
        scene_id="scene_ai_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert scene == AnimationScene(
        scene_id="scene_ai_1",
        duration_seconds=8.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="idle",
                        start_seconds=0.0,
                        duration_seconds=2.0,
                    ),
                    AnimationAction(
                        action="turn_head",
                        start_seconds=2.0,
                        duration_seconds=1.0,
                    ),
                    AnimationAction(
                        action="wave",
                        start_seconds=3.0,
                        duration_seconds=3.0,
                    ),
                    AnimationAction(
                        action="step_forward",
                        start_seconds=6.0,
                        duration_seconds=2.0,
                    ),
                ),
            ),
        ),
    )


def test_agent_prompt_contains_constraints() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = AnimatorAgent(
        llm,
        _registry(),
    )

    agent.generate_plan(
        "Momo waves and steps forward.",
        scene_id="scene_ai_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert len(llm.calls) == 1

    prompt, system_prompt, response_schema = llm.calls[0]

    assert "Momo waves and steps forward." in prompt
    assert "scene_ai_1" in prompt
    assert "momo" in prompt
    assert "8.0" in prompt

    for action in (
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    ):
        assert action in prompt

    assert system_prompt is not None
    assert "Never generate Python" in system_prompt
    assert "Return ONLY valid JSON" in system_prompt

    assert response_schema is not None

    properties = response_schema["properties"]

    assert isinstance(
        properties,
        dict,
    )

    assert properties["scene_id"]["const"] == "scene_ai_1"
    assert properties["character_id"]["const"] == "momo"
    assert properties["duration_seconds"]["const"] == 8.0

    definitions = response_schema["$defs"]

    assert isinstance(
        definitions,
        dict,
    )

    action_definition = definitions[
        "AnimatorActionPlan"
    ]

    action_properties = action_definition[
        "properties"
    ]

    assert action_properties[
        "action"
    ]["enum"] == [
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    ]


def test_agent_rejects_empty_intent_before_llm() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = AnimatorAgent(
        llm,
        _registry(),
    )

    with pytest.raises(
        ValueError,
        match="intent",
    ):
        agent.generate_scene(
            "   ",
            scene_id="scene_ai_1",
            character_id="momo",
            duration_seconds=8.0,
        )

    assert llm.calls == []


def test_agent_rejects_unregistered_character() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = AnimatorAgent(
        llm,
        _registry(),
    )

    with pytest.raises(
        AnimatorAgentError,
        match="not registered",
    ):
        agent.generate_scene(
            "Someone waves.",
            scene_id="scene_ai_1",
            character_id="unknown",
            duration_seconds=8.0,
        )

    assert llm.calls == []


def test_agent_translates_llm_failure() -> None:
    llm = FakeLLM(
        "",
        error=RuntimeError(
            "offline"
        ),
    )

    agent = AnimatorAgent(
        llm,
        _registry(),
    )

    with pytest.raises(
        AnimatorAgentError,
        match="LLM generation failed",
    ):
        agent.generate_scene(
            "Momo waves.",
            scene_id="scene_ai_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_invalid_json() -> None:
    agent = AnimatorAgent(
        FakeLLM(
            "not-json"
        ),
        _registry(),
    )

    with pytest.raises(
        AnimatorAgentError,
        match="invalid plan JSON",
    ):
        agent.generate_scene(
            "Momo waves.",
            scene_id="scene_ai_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_unsupported_action() -> None:
    data = json.loads(
        _valid_response()
    )

    data["actions"][0][
        "action"
    ] = "backflip"

    agent = AnimatorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        AnimatorAgentError,
        match="unsupported action",
    ):
        agent.generate_scene(
            "Momo performs something.",
            scene_id="scene_ai_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_changed_character_identity() -> None:
    data = json.loads(
        _valid_response()
    )

    data["character_id"] = "someone_else"

    agent = AnimatorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        AnimatorAgentError,
        match="character ID",
    ):
        agent.generate_scene(
            "Momo waves.",
            scene_id="scene_ai_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_changed_duration() -> None:
    data = json.loads(
        _valid_response()
    )

    data["duration_seconds"] = 9.0

    agent = AnimatorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        AnimatorAgentError,
        match="scene duration",
    ):
        agent.generate_scene(
            "Momo waves.",
            scene_id="scene_ai_1",
            character_id="momo",
            duration_seconds=8.0,
        )