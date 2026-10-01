"""Tests for Director-to-Animator Studio orchestration."""

from __future__ import annotations

import json

from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.application.animator_agent import (
    AnimatorAgent,
)
from kernel.application.directed_animation import (
    DirectedAnimationService,
)
from kernel.application.director_agent import (
    DirectorAgent,
)
from kernel.capabilities.models import (
    CapabilityRegistry,
    CharacterCapability,
)


class SequencedFakeLLM:
    """Return deterministic responses in Director-then-Animator order."""

    def __init__(
        self,
        responses: tuple[str, ...],
    ) -> None:
        self._responses = list(
            responses
        )

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

        if not self._responses:
            raise RuntimeError(
                "No fake LLM response remains."
            )

        return self._responses.pop(0)


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


def _director_response() -> str:
    return json.dumps(
        {
            "scene_id": "phase4c_scene_1",
            "duration_seconds": 8.0,
            "character_id": "momo",
            "scene_objective": (
                "Show Momo recognizing an old friend."
            ),
            "emotion": (
                "uncertainty to warm recognition"
            ),
            "shot": {
                "framing": "close_up",
                "camera_intent": "push_in",
                "pacing": "slow",
            },
            "performance_intent": (
                "Momo notices the person, hesitates, "
                "recognizes them, greets them warmly, "
                "then approaches cautiously."
            ),
        }
    )


def _animator_response() -> str:
    return json.dumps(
        {
            "scene_id": "phase4c_scene_1",
            "duration_seconds": 8.0,
            "character_id": "momo",
            "actions": [
                {
                    "action": "idle",
                    "start_seconds": 0.0,
                    "duration_seconds": 1.0,
                },
                {
                    "action": "turn_head",
                    "start_seconds": 1.0,
                    "duration_seconds": 0.5,
                },
                {
                    "action": "wave",
                    "start_seconds": 1.5,
                    "duration_seconds": 0.5,
                },
                {
                    "action": "step_forward",
                    "start_seconds": 2.0,
                    "duration_seconds": 1.0,
                },
            ],
        }
    )


def _service(
    llm: SequencedFakeLLM,
) -> DirectedAnimationService:
    registry = _registry()

    return DirectedAnimationService(
        DirectorAgent(
            llm,
            registry,
        ),
        AnimatorAgent(
            llm,
            registry,
        ),
    )


def test_director_to_animator_generates_trusted_scene() -> None:
    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    result = _service(
        llm
    ).generate(
        (
            "Momo unexpectedly sees an old friend. "
            "Begin uncertain and end warmly."
        ),
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert len(llm.calls) == 2

    assert result.director_plan.scene_id == "phase4c_scene_1"

    assert (
        result.director_plan.shot.camera_intent
        == "push_in"
    )

    assert tuple(
        action.action
        for action in result.animator_plan.actions
    ) == (
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    )

    assert result.animation_scene == AnimationScene(
        scene_id="phase4c_scene_1",
        duration_seconds=8.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="idle",
                        start_seconds=0.0,
                        duration_seconds=1.0,
                    ),
                    AnimationAction(
                        action="turn_head",
                        start_seconds=1.0,
                        duration_seconds=0.5,
                    ),
                    AnimationAction(
                        action="wave",
                        start_seconds=1.5,
                        duration_seconds=0.5,
                    ),
                    AnimationAction(
                        action="step_forward",
                        start_seconds=2.0,
                        duration_seconds=1.0,
                    ),
                ),
            ),
        ),
    )


def test_animator_receives_director_performance_context() -> None:
    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    _service(
        llm
    ).generate(
        "Momo recognizes someone important.",
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert len(llm.calls) == 2

    director_prompt = llm.calls[0][0]
    animator_prompt = llm.calls[1][0]

    assert (
        "Momo recognizes someone important."
        in director_prompt
    )

    assert (
        "Show Momo recognizing an old friend."
        in animator_prompt
    )

    assert (
        "uncertainty to warm recognition"
        in animator_prompt
    )

    assert (
        "greets them warmly"
        in animator_prompt
    )

    assert (
        "framing=close_up"
        in animator_prompt
    )

    assert (
        "camera_intent=push_in"
        in animator_prompt
    )

    assert (
        "pacing=slow"
        in animator_prompt
    )


def test_camera_direction_is_context_not_animation_capability() -> None:
    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    result = _service(
        llm
    ).generate(
        "Direct a cautious reunion.",
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    animation_actions = tuple(
        action.action
        for action in result.animator_plan.actions
    )

    assert "push_in" not in animation_actions
    assert "close_up" not in animation_actions
    assert "slow" not in animation_actions

    animator_prompt = llm.calls[1][0]

    assert (
        "Treat framing and camera intent as context only"
        in animator_prompt
    )


def test_agents_are_called_sequentially() -> None:
    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    result = _service(
        llm
    ).generate(
        "Momo cautiously recognizes an old friend.",
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert len(llm.calls) == 2

    director_system_prompt = llm.calls[0][1]
    animator_system_prompt = llm.calls[1][1]

    assert director_system_prompt is not None
    assert animator_system_prompt is not None

    assert (
        "Studio Director Agent"
        in director_system_prompt
    )

    assert (
        "Studio Animator Agent"
        in animator_system_prompt
    )

    assert result.director_plan.character_id == "momo"
    assert result.animator_plan.character_id == "momo"


def test_handoff_preserves_trusted_request_identity() -> None:
    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    result = _service(
        llm
    ).generate(
        "Momo sees someone familiar.",
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert (
        result.director_plan.scene_id
        == result.animator_plan.scene_id
        == result.animation_scene.scene_id
        == "phase4c_scene_1"
    )

    assert (
        result.director_plan.character_id
        == result.animator_plan.character_id
        == "momo"
    )

    assert (
        result.director_plan.duration_seconds
        == result.animator_plan.duration_seconds
        == result.animation_scene.duration_seconds
        == 8.0
    )


def test_director_and_animator_receive_same_persistent_identity_context() -> None:
    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    _service(
        llm
    ).generate(
        "Momo recognizes an old friend.",
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
    )

    assert len(llm.calls) == 2

    director_prompt = llm.calls[0][0]
    animator_prompt = llm.calls[1][0]

    for prompt in (
        director_prompt,
        animator_prompt,
    ):
        assert "Persistent character identity context:" in prompt
        assert "Display name: Momo" in prompt
        assert "recognizable silhouette" in prompt
        assert "deliberate movement" in prompt


def test_directed_animation_forwards_one_variant_to_both_agents() -> None:
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

    llm = SequencedFakeLLM(
        (
            _director_response(),
            _animator_response(),
        )
    )

    registry = _registry()

    service = DirectedAnimationService(
        DirectorAgent(
            llm,
            registry,
            catalog=catalog,
        ),
        AnimatorAgent(
            llm,
            registry,
            catalog=catalog,
        ),
    )

    result = service.generate(
        "Momo recognizes an old friend during winter.",
        scene_id="phase4c_scene_1",
        character_id="momo",
        duration_seconds=8.0,
        variant_id="winter",
    )

    assert len(llm.calls) == 2

    director_prompt = llm.calls[0][0]
    animator_prompt = llm.calls[1][0]

    for prompt in (
        director_prompt,
        animator_prompt,
    ):
        assert "Variant ID: winter" in prompt
        assert "Momo - Winter" in prompt
        assert "winter coat" in prompt

    assert result.director_plan.character_id == "momo"
    assert result.animator_plan.character_id == "momo"
