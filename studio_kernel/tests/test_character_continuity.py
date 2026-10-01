"""Cross-shot continuity tests for persistent Studio characters."""

from __future__ import annotations

import json

from kernel.adapters.filesystem.character_catalog_store import (
    load_character_catalog,
    save_character_catalog,
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
from kernel.characters import (
    CharacterCatalog,
    CharacterVariant,
    CharacterVariantAppearance,
    MOMO_DEFAULT_VARIANT,
    MOMO_IDENTITY,
)


class SequencedFakeLLM:
    """Return deterministic responses while recording prompts."""

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

        return self._responses.pop(
            0
        )


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


def _catalog() -> CharacterCatalog:
    winter = CharacterVariant(
        character_id="momo",
        variant_id="winter",
        display_name="Momo - Winter",
        appearance=CharacterVariantAppearance(
            summary=(
                "Momo wearing her winter appearance."
            ),
            descriptors=(
                "winter coat",
                "winter scarf",
            ),
        ),
    )

    return CharacterCatalog(
        identities=(
            MOMO_IDENTITY,
        ),
        variants=(
            MOMO_DEFAULT_VARIANT,
            winter,
        ),
    )


def _director_response(
    scene_id: str,
) -> str:
    return json.dumps(
        {
            "scene_id": scene_id,
            "duration_seconds": 8.0,
            "character_id": "momo",
            "scene_objective": (
                "Momo recognizes an old friend."
            ),
            "emotion": (
                "cautious recognition becoming warm"
            ),
            "shot": {
                "framing": "medium",
                "camera_intent": "push_in",
                "pacing": "slow",
            },
            "performance_intent": (
                "Begin reserved, recognize the friend, "
                "then soften into a warm response."
            ),
        }
    )


def _animator_response(
    scene_id: str,
) -> str:
    return json.dumps(
        {
            "scene_id": scene_id,
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
                    "duration_seconds": 2.0,
                },
                {
                    "action": "wave",
                    "start_seconds": 4.0,
                    "duration_seconds": 2.0,
                },
                {
                    "action": "step_forward",
                    "start_seconds": 6.0,
                    "duration_seconds": 2.0,
                },
            ],
        }
    )


def _run_shot(
    *,
    catalog: CharacterCatalog,
    scene_id: str,
    variant_id: str,
):
    llm = SequencedFakeLLM(
        (
            _director_response(
                scene_id
            ),
            _animator_response(
                scene_id
            ),
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
        "Momo encounters an old friend.",
        scene_id=scene_id,
        character_id="momo",
        duration_seconds=8.0,
        variant_id=variant_id,
    )

    return result, llm


def test_separate_studio_runs_preserve_character_context_across_shots(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "characters"
        / "catalog.json"
    )

    save_character_catalog(
        _catalog(),
        path,
    )

    first_run_catalog = load_character_catalog(
        path
    )

    second_run_catalog = load_character_catalog(
        path
    )

    assert first_run_catalog == second_run_catalog
    assert first_run_catalog is not second_run_catalog

    first_result, first_llm = _run_shot(
        catalog=first_run_catalog,
        scene_id="continuity_shot_1",
        variant_id="winter",
    )

    second_result, second_llm = _run_shot(
        catalog=second_run_catalog,
        scene_id="continuity_shot_2",
        variant_id="winter",
    )

    assert (
        first_result.director_plan.character_id
        == second_result.director_plan.character_id
        == "momo"
    )

    assert (
        first_result.animator_plan.character_id
        == second_result.animator_plan.character_id
        == "momo"
    )

    prompts = (
        first_llm.calls[0][0],
        first_llm.calls[1][0],
        second_llm.calls[0][0],
        second_llm.calls[1][0],
    )

    stable_identity_context = (
        "Display name: Momo",
        "recognizable silhouette",
        "consistent facial proportions",
        "stable core color identity",
        "observant",
        "warm",
        "deliberate movement",
    )

    stable_variant_context = (
        "Variant ID: winter",
        "Variant name: Momo - Winter",
        "winter coat",
        "winter scarf",
    )

    for prompt in prompts:
        for token in stable_identity_context:
            assert token in prompt

        for token in stable_variant_context:
            assert token in prompt


def test_variant_can_change_between_shots_without_changing_identity(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "catalog.json"
    )

    save_character_catalog(
        _catalog(),
        path,
    )

    first_catalog = load_character_catalog(
        path
    )

    second_catalog = load_character_catalog(
        path
    )

    first_result, first_llm = _run_shot(
        catalog=first_catalog,
        scene_id="continuity_default",
        variant_id="default",
    )

    second_result, second_llm = _run_shot(
        catalog=second_catalog,
        scene_id="continuity_winter",
        variant_id="winter",
    )

    assert (
        first_result.director_plan.character_id
        == second_result.director_plan.character_id
        == "momo"
    )

    default_prompts = (
        first_llm.calls[0][0],
        first_llm.calls[1][0],
    )

    winter_prompts = (
        second_llm.calls[0][0],
        second_llm.calls[1][0],
    )

    for prompt in default_prompts:
        assert "Display name: Momo" in prompt
        assert "recognizable silhouette" in prompt
        assert "deliberate movement" in prompt
        assert "Variant ID: default" in prompt

    for prompt in winter_prompts:
        assert "Display name: Momo" in prompt
        assert "recognizable silhouette" in prompt
        assert "deliberate movement" in prompt
        assert "Variant ID: winter" in prompt

    assert (
        "Variant ID: winter"
        not in first_llm.calls[0][0]
    )

    assert (
        "Variant ID: default"
        not in second_llm.calls[0][0]
    )


def test_cross_shot_variant_context_does_not_expand_animation_ir(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "catalog.json"
    )

    save_character_catalog(
        _catalog(),
        path,
    )

    catalog = load_character_catalog(
        path
    )

    result, _ = _run_shot(
        catalog=catalog,
        scene_id="continuity_ir_boundary",
        variant_id="winter",
    )

    character_animation = (
        result.animation_scene.characters[0]
    )

    assert character_animation.character_id == "momo"

    assert not hasattr(
        character_animation,
        "variant_id",
    )

    assert not hasattr(
        character_animation,
        "appearance",
    )

    assert not hasattr(
        character_animation,
        "performance",
    )
