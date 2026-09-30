"""Tests for Studio Animator plan contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.application.animator_plan import (
    AnimatorPlanParseError,
    animation_scene_from_plan,
    animator_plan_from_json,
)
from kernel.capabilities.loader import (
    load_capability_registry,
)
from kernel.capabilities.validator import (
    validate_animation_capabilities,
)


CAPABILITIES_PATH = (
    Path(__file__).parents[1]
    / "kernel"
    / "assets"
    / "capabilities.json"
)


def _valid_plan_json() -> str:
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


def test_animator_plan_parses_valid_json() -> None:
    plan = animator_plan_from_json(
        _valid_plan_json()
    )

    assert plan.scene_id == "scene_ai_1"
    assert plan.duration_seconds == 8.0
    assert plan.character_id == "momo"

    assert tuple(
        action.action
        for action in plan.actions
    ) == (
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    )


def test_animator_plan_rejects_extra_fields() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["unexpected"] = "unsafe"

    with pytest.raises(
        AnimatorPlanParseError
    ):
        animator_plan_from_json(
            json.dumps(data)
        )


def test_animator_plan_rejects_negative_start() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["actions"][0][
        "start_seconds"
    ] = -1.0

    with pytest.raises(
        AnimatorPlanParseError
    ):
        animator_plan_from_json(
            json.dumps(data)
        )


def test_animator_plan_rejects_action_beyond_scene() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["actions"][-1][
        "duration_seconds"
    ] = 4.0

    with pytest.raises(
        AnimatorPlanParseError
    ):
        animator_plan_from_json(
            json.dumps(data)
        )


def test_animator_plan_converts_to_animation_ir() -> None:
    scene = animation_scene_from_plan(
        animator_plan_from_json(
            _valid_plan_json()
        )
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


def test_phase_3_registry_matches_real_actions() -> None:
    registry = load_capability_registry(
        CAPABILITIES_PATH
    )

    momo = registry.get_character(
        "momo"
    )

    assert momo is not None

    assert momo.actions == (
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    )


def test_valid_plan_passes_capability_validation() -> None:
    registry = load_capability_registry(
        CAPABILITIES_PATH
    )

    scene = animation_scene_from_plan(
        animator_plan_from_json(
            _valid_plan_json()
        )
    )

    validate_animation_capabilities(
        scene,
        registry,
    )