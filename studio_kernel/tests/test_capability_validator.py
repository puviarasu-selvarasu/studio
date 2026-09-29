"""Tests for Animation IR capability validation."""

from __future__ import annotations

import pytest

from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.capabilities import (
    CapabilityRegistry,
    CapabilityValidationError,
    CharacterCapability,
    validate_animation_capabilities,
)


def test_supported_action_passes() -> None:
    """A supported character action should pass validation."""
    scene = AnimationScene(
        scene_id="scene_001",
        duration_seconds=5.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="wave",
                        start_seconds=1.0,
                        duration_seconds=2.0,
                    ),
                ),
            ),
        ),
    )

    registry = CapabilityRegistry(
        characters=(
            CharacterCapability(
                character_id="momo",
                actions=("idle", "wave"),
            ),
        ),
    )

    validate_animation_capabilities(scene, registry)


def test_unsupported_action_fails() -> None:
    """An unsupported character action should fail validation."""
    scene = AnimationScene(
        scene_id="scene_001",
        duration_seconds=5.0,
        characters=(
            CharacterAnimation(
                character_id="momo",
                actions=(
                    AnimationAction(
                        action="jump",
                        start_seconds=1.0,
                        duration_seconds=2.0,
                    ),
                ),
            ),
        ),
    )

    registry = CapabilityRegistry(
        characters=(
            CharacterCapability(
                character_id="momo",
                actions=("idle", "wave"),
            ),
        ),
    )

    with pytest.raises(CapabilityValidationError) as exc_info:
        validate_animation_capabilities(scene, registry)

    assert exc_info.value.character_id == "momo"
    assert exc_info.value.action == "jump"
    assert "does not support" in str(exc_info.value)


def test_unknown_character_fails() -> None:
    """An animation request for an unregistered character should fail."""
    scene = AnimationScene(
        scene_id="scene_001",
        duration_seconds=5.0,
        characters=(
            CharacterAnimation(
                character_id="akira",
                actions=(
                    AnimationAction(
                        action="wave",
                        start_seconds=1.0,
                        duration_seconds=2.0,
                    ),
                ),
            ),
        ),
    )

    registry = CapabilityRegistry(
        characters=(
            CharacterCapability(
                character_id="momo",
                actions=("idle", "wave"),
            ),
        ),
    )

    with pytest.raises(CapabilityValidationError) as exc_info:
        validate_animation_capabilities(scene, registry)

    assert exc_info.value.character_id == "akira"
    assert exc_info.value.action == ""
    assert "not registered" in str(exc_info.value)


def test_multiple_supported_actions_pass() -> None:
    """Multiple supported actions for one character should pass."""
    scene = AnimationScene(
        scene_id="scene_001",
        duration_seconds=10.0,
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
                        action="walk",
                        start_seconds=2.0,
                        duration_seconds=3.0,
                    ),
                    AnimationAction(
                        action="blink",
                        start_seconds=5.0,
                        duration_seconds=1.0,
                    ),
                ),
            ),
        ),
    )

    registry = CapabilityRegistry(
        characters=(
            CharacterCapability(
                character_id="momo",
                actions=("idle", "blink", "walk"),
            ),
        ),
    )

    validate_animation_capabilities(scene, registry)
