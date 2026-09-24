"""Tests for Studio Animation IR."""

from __future__ import annotations

from kernel.animation_ir import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
    validate_animation_scene,
)


def test_valid_animation_scene_has_no_errors() -> None:
    """A valid scene should pass structural validation."""
    scene = AnimationScene(
        scene_id="scene_01",
        duration_seconds=8.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="wave",
                        start_seconds=1.0,
                        duration_seconds=2.0,
                    ),
                    AnimationAction(
                        action="blink",
                        start_seconds=4.0,
                        duration_seconds=0.3,
                    ),
                ),
            ),
        ),
    )

    errors = validate_animation_scene(scene)

    assert errors == []


def test_empty_scene_id_is_invalid() -> None:
    """An empty scene ID should fail validation."""
    scene = AnimationScene(
        scene_id="",
        duration_seconds=5.0,
    )

    errors = validate_animation_scene(scene)

    assert any(error.field == "scene_id" for error in errors)


def test_negative_action_start_is_invalid() -> None:
    """Negative action start times should fail validation."""
    scene = AnimationScene(
        scene_id="scene_01",
        duration_seconds=5.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="wave",
                        start_seconds=-1.0,
                        duration_seconds=1.0,
                    ),
                ),
            ),
        ),
    )

    errors = validate_animation_scene(scene)

    assert any(
        error.field.endswith(".start_seconds")
        for error in errors
    )


def test_action_cannot_extend_beyond_scene() -> None:
    """Actions must finish within the scene duration."""
    scene = AnimationScene(
        scene_id="scene_01",
        duration_seconds=5.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="wave",
                        start_seconds=4.0,
                        duration_seconds=2.0,
                    ),
                ),
            ),
        ),
    )

    errors = validate_animation_scene(scene)

    assert any(
        "beyond the scene duration" in error.message
        for error in errors
    )


def test_zero_action_duration_is_invalid() -> None:
    """An action must have a positive duration."""
    scene = AnimationScene(
        scene_id="scene_01",
        duration_seconds=5.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="blink",
                        start_seconds=1.0,
                        duration_seconds=0.0,
                    ),
                ),
            ),
        ),
    )

    errors = validate_animation_scene(scene)

    assert any(
        error.field.endswith(".duration_seconds")
        for error in errors
    )