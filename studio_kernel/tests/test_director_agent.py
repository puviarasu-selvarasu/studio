"""Tests for Studio AI Director Agent."""

from __future__ import annotations

import json

import pytest

from kernel.application.director_agent import (
    DirectorAgent,
    DirectorAgentError,
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
            "scene_id": "director_scene_1",
            "duration_seconds": 8.0,
            "character_id": "momo",
            "scene_objective": (
                "Show Momo unexpectedly recognizing "
                "someone familiar."
            ),
            "emotion": (
                "uncertainty to warm recognition"
            ),
            "shot": {
                "framing": "medium",
                "camera_intent": "push_in",
                "pacing": "slow",
            },
            "performance_intent": (
                "Momo notices someone to her right, "
                "hesitates, recognizes them, greets them, "
                "then cautiously approaches."
            ),
        }
    )


def test_agent_generates_validated_director_plan() -> None:
    agent = DirectorAgent(
        FakeLLM(
            _valid_response()
        ),
        _registry(),
    )

    plan = agent.generate_plan(
        (
            "Momo unexpectedly sees an old friend. "
            "Begin uncertain and end warmly."
        ),
        scene_id="director_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert plan.scene_id == "director_scene_1"
    assert plan.duration_seconds == 8.0
    assert plan.character_id == "momo"

    assert plan.shot.framing == "medium"
    assert plan.shot.camera_intent == "push_in"
    assert plan.shot.pacing == "slow"

    assert "recognizes" in plan.performance_intent


def test_agent_prompt_contains_director_constraints() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = DirectorAgent(
        llm,
        _registry(),
    )

    scene_intent = (
        "Momo unexpectedly sees an old friend."
    )

    agent.generate_plan(
        scene_intent,
        scene_id="director_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert len(llm.calls) == 1

    (
        prompt,
        system_prompt,
        response_schema,
    ) = llm.calls[0]

    assert scene_intent in prompt
    assert "director_scene_1" in prompt
    assert "momo" in prompt
    assert "8.0" in prompt

    for framing in (
        "wide",
        "medium",
        "close_up",
    ):
        assert framing in prompt

    for camera_intent in (
        "static",
        "push_in",
        "pull_back",
        "pan_left",
        "pan_right",
    ):
        assert camera_intent in prompt

    for pacing in (
        "slow",
        "moderate",
        "fast",
    ):
        assert pacing in prompt

    assert system_prompt is not None
    assert "Return ONLY valid JSON" in system_prompt
    assert "not implementing animation" in system_prompt
    assert "Python" in system_prompt
    assert "Blender code" in system_prompt

    assert response_schema is not None

    properties = response_schema[
        "properties"
    ]

    assert isinstance(
        properties,
        dict,
    )

    assert (
        properties["scene_id"]["const"]
        == "director_scene_1"
    )

    assert (
        properties["character_id"]["const"]
        == "momo"
    )

    assert (
        properties["duration_seconds"]["const"]
        == 8.0
    )


def test_response_schema_preserves_shot_enums() -> None:
    schema = DirectorAgent._response_schema(
        scene_id="director_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    definitions = schema[
        "$defs"
    ]

    assert isinstance(
        definitions,
        dict,
    )

    shot_definition = definitions[
        "DirectorShotPlan"
    ]

    shot_properties = shot_definition[
        "properties"
    ]

    assert shot_properties[
        "framing"
    ]["enum"] == [
        "wide",
        "medium",
        "close_up",
    ]

    assert shot_properties[
        "camera_intent"
    ]["enum"] == [
        "static",
        "push_in",
        "pull_back",
        "pan_left",
        "pan_right",
    ]

    assert shot_properties[
        "pacing"
    ]["enum"] == [
        "slow",
        "moderate",
        "fast",
    ]


def test_agent_rejects_empty_scene_intent_before_llm() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = DirectorAgent(
        llm,
        _registry(),
    )

    with pytest.raises(
        ValueError,
        match="intent",
    ):
        agent.generate_plan(
            "   ",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )

    assert llm.calls == []


def test_agent_rejects_unregistered_character_before_llm() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = DirectorAgent(
        llm,
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="not registered",
    ):
        agent.generate_plan(
            "Someone enters the scene.",
            scene_id="director_scene_1",
            character_id="unknown",
            duration_seconds=8.0,
        )

    assert llm.calls == []


def test_agent_translates_llm_failure() -> None:
    agent = DirectorAgent(
        FakeLLM(
            "",
            error=RuntimeError(
                "offline"
            ),
        ),
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="LLM generation failed",
    ):
        agent.generate_plan(
            "Momo recognizes someone.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_invalid_json() -> None:
    agent = DirectorAgent(
        FakeLLM(
            "not-json"
        ),
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="invalid plan JSON",
    ):
        agent.generate_plan(
            "Momo recognizes someone.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_extra_ai_field() -> None:
    data = json.loads(
        _valid_response()
    )

    data["blender_python"] = "unsafe"

    agent = DirectorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="invalid plan JSON",
    ):
        agent.generate_plan(
            "Momo recognizes someone.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_changed_scene_identity() -> None:
    data = json.loads(
        _valid_response()
    )

    data["scene_id"] = "changed_scene"

    agent = DirectorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="scene ID",
    ):
        agent.generate_plan(
            "Momo recognizes someone.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_changed_character_identity() -> None:
    data = json.loads(
        _valid_response()
    )

    data["character_id"] = "someone_else"

    agent = DirectorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="character ID",
    ):
        agent.generate_plan(
            "Momo recognizes someone.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_rejects_changed_duration() -> None:
    data = json.loads(
        _valid_response()
    )

    data["duration_seconds"] = 12.0

    agent = DirectorAgent(
        FakeLLM(
            json.dumps(data)
        ),
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="scene duration",
    ):
        agent.generate_plan(
            "Momo recognizes someone.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
        )


def test_agent_prompt_includes_persistent_character_identity_context() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = DirectorAgent(
        llm,
        _registry(),
    )

    agent.generate_plan(
        "Momo notices someone important.",
        scene_id="director_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    prompt = llm.calls[0][0]

    assert "Persistent character identity context:" in prompt
    assert "Display name: Momo" in prompt
    assert "recognizable silhouette" in prompt
    assert "Observant and warm" in prompt
    assert "deliberate movement" in prompt
    assert "production variant" in prompt


def test_director_rejects_capability_without_character_identity_before_llm() -> None:
    from kernel.characters import CharacterCatalog

    llm = FakeLLM(
        _valid_response()
    )

    registry = CapabilityRegistry(
        characters=(
            CharacterCapability(
                character_id="akira",
                actions=(
                    "idle",
                ),
            ),
        )
    )

    agent = DirectorAgent(
        llm,
        registry,
        catalog=CharacterCatalog(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="identity.*not registered",
    ):
        agent.generate_plan(
            "Akira waits quietly.",
            scene_id="director_scene_identity",
            character_id="akira",
            duration_seconds=8.0,
        )

    assert llm.calls == []


def test_director_supports_explicit_character_variant_selection() -> None:
    from kernel.characters import (
        CharacterCatalog,
        CharacterVariant,
        CharacterVariantAppearance,
        MOMO_DEFAULT_VARIANT,
        MOMO_IDENTITY,
    )

    winter = CharacterVariant(
        character_id="momo",
        variant_id="winter",
        display_name="Momo - Winter",
        appearance=CharacterVariantAppearance(
            summary="Momo wearing her winter appearance.",
            descriptors=(
                "winter coat",
                "winter scarf",
            ),
        ),
    )

    catalog = CharacterCatalog(
        identities=(
            MOMO_IDENTITY,
        ),
        variants=(
            MOMO_DEFAULT_VARIANT,
            winter,
        ),
    )

    llm = FakeLLM(
        _valid_response()
    )

    agent = DirectorAgent(
        llm,
        _registry(),
        catalog=catalog,
    )

    agent.generate_plan(
        "Momo meets a friend in winter.",
        scene_id="director_scene_1",
        character_id="momo",
        duration_seconds=8.0,
        variant_id="winter",
    )

    prompt = llm.calls[0][0]

    assert "Selected character variant:" in prompt
    assert "Variant ID: winter" in prompt
    assert "Variant name: Momo - Winter" in prompt
    assert "winter coat" in prompt
    assert "winter scarf" in prompt


def test_director_rejects_unknown_character_variant_before_llm() -> None:
    llm = FakeLLM(
        _valid_response()
    )

    agent = DirectorAgent(
        llm,
        _registry(),
    )

    with pytest.raises(
        DirectorAgentError,
        match="variant.*not registered",
    ):
        agent.generate_plan(
            "Momo waits.",
            scene_id="director_scene_1",
            character_id="momo",
            duration_seconds=8.0,
            variant_id="unknown",
        )

    assert llm.calls == []
