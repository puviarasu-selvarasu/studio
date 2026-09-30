"""Tests for trusted Animation IR to Blender semantic dispatch."""

from __future__ import annotations

import inspect

import pytest

from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.adapters.blender.semantic_dispatcher import (
    BlenderActionFunctions,
    SemanticDispatchError,
    compile_animation_scene,
    execute_animation_scene,
)


def _scene() -> AnimationScene:
    return AnimationScene(
        scene_id="scene_ai_1",
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


def test_compile_real_ai_plan_to_frames() -> None:
    commands = compile_animation_scene(
        _scene(),
        fps=24,
    )

    assert tuple(
        (
            command.action,
            command.start_frame,
            command.duration_frames,
        )
        for command in commands
    ) == (
        (
            "idle",
            1,
            24,
        ),
        (
            "turn_head",
            25,
            12,
        ),
        (
            "wave",
            37,
            12,
        ),
        (
            "step_forward",
            49,
            24,
        ),
    )


def test_compile_uses_deterministic_action_defaults() -> None:
    commands = compile_animation_scene(
        _scene()
    )

    assert commands[0].direction is None
    assert commands[0].side is None
    assert commands[0].distance is None

    assert commands[1].direction == "right"
    assert commands[2].side == "L"
    assert commands[3].distance == 0.75


def test_execute_calls_only_explicit_trusted_functions() -> None:
    calls: list[
        tuple[str, dict[str, object]]
    ] = []

    def record(
        name: str,
    ):
        def action(
            **kwargs: object,
        ) -> None:
            calls.append(
                (
                    name,
                    kwargs,
                )
            )

        return action

    functions = BlenderActionFunctions(
        idle=record("idle"),
        turn_head=record("turn_head"),
        wave=record("wave"),
        step_forward=record("step_forward"),
    )

    execute_animation_scene(
        _scene(),
        armature_name="StudioShotRig",
        action_functions=functions,
    )

    assert calls == [
        (
            "idle",
            {
                "armature_name": "StudioShotRig",
                "start_frame": 1,
                "duration_frames": 24,
            },
        ),
        (
            "turn_head",
            {
                "armature_name": "StudioShotRig",
                "start_frame": 25,
                "duration_frames": 12,
                "direction": "right",
            },
        ),
        (
            "wave",
            {
                "armature_name": "StudioShotRig",
                "start_frame": 37,
                "duration_frames": 12,
                "side": "L",
            },
        ),
        (
            "step_forward",
            {
                "armature_name": "StudioShotRig",
                "start_frame": 49,
                "duration_frames": 24,
                "distance": 0.75,
            },
        ),
    ]


def test_dispatch_rejects_unsupported_action() -> None:
    scene = AnimationScene(
        scene_id="bad",
        duration_seconds=2.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="backflip",
                        start_seconds=0.0,
                        duration_seconds=1.0,
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(
        SemanticDispatchError,
        match="Unsupported semantic action",
    ):
        compile_animation_scene(
            scene
        )


def test_dispatch_rejects_action_shorter_than_mechanic_minimum() -> None:
    scene = AnimationScene(
        scene_id="too_short",
        duration_seconds=2.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="wave",
                        start_seconds=0.0,
                        duration_seconds=0.1,
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(
        SemanticDispatchError,
        match="at least 8 frames",
    ):
        compile_animation_scene(
            scene,
            fps=24,
        )


def test_dispatch_requires_single_character() -> None:
    scene = AnimationScene(
        scene_id="empty",
        duration_seconds=1.0,
        characters=(),
    )

    with pytest.raises(
        SemanticDispatchError,
        match="exactly one",
    ):
        compile_animation_scene(
            scene
        )


def test_dispatch_rejects_invalid_fps() -> None:
    with pytest.raises(
        SemanticDispatchError,
        match="FPS",
    ):
        compile_animation_scene(
            _scene(),
            fps=0,
        )


def test_dispatch_rejects_empty_armature_name() -> None:
    functions = BlenderActionFunctions(
        idle=lambda **kwargs: None,
        turn_head=lambda **kwargs: None,
        wave=lambda **kwargs: None,
        step_forward=lambda **kwargs: None,
    )

    with pytest.raises(
        SemanticDispatchError,
        match="Armature",
    ):
        execute_animation_scene(
            _scene(),
            armature_name="   ",
            action_functions=functions,
        )


def test_dispatcher_does_not_use_dynamic_execution() -> None:
    import kernel.adapters.blender.semantic_dispatcher as dispatcher

    source = inspect.getsource(
        dispatcher
    )

    assert "eval(" not in source
    assert "exec(" not in source
    assert "getattr(" not in source
    assert "__import__(" not in source
