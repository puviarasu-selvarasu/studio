"""Translate validated Animation IR into trusted Blender actions."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Callable

from kernel.animation_ir.models import AnimationScene
from kernel.animation_ir.validator import validate_animation_scene


class SemanticDispatchError(Exception):
    """Represent an invalid or unsupported Blender dispatch request."""


ActionCallable = Callable[..., None]


@dataclass(frozen=True)
class BlenderActionFunctions:
    """Contain the only trusted semantic action functions."""

    idle: ActionCallable
    turn_head: ActionCallable
    wave: ActionCallable
    step_forward: ActionCallable


@dataclass(frozen=True)
class BlenderActionCommand:
    """Describe one trusted frame-level Blender action command."""

    action: str
    start_frame: int
    duration_frames: int
    direction: str | None = None
    side: str | None = None
    distance: float | None = None

    @property
    def end_frame(self) -> int:
        """Return the inclusive final frame."""

        return (
            self.start_frame
            + self.duration_frames
            - 1
        )


def _seconds_to_start_frame(
    seconds: float,
    fps: int,
) -> int:
    """Convert timeline seconds to a one-based Blender frame."""

    return floor(
        seconds * fps
    ) + 1


def _seconds_to_duration_frames(
    seconds: float,
    fps: int,
) -> int:
    """Convert positive duration seconds into deterministic frames."""

    return max(
        1,
        floor(
            seconds * fps
            + 0.5
        ),
    )


def compile_animation_scene(
    scene: AnimationScene,
    *,
    fps: int = 24,
) -> tuple[BlenderActionCommand, ...]:
    """Compile trusted single-character Animation IR into commands."""

    if fps <= 0:
        raise SemanticDispatchError(
            "FPS must be greater than zero."
        )

    validation_errors = validate_animation_scene(
        scene
    )

    if validation_errors:
        details = "; ".join(
            f"{error.field}: {error.message}"
            for error in validation_errors
        )

        raise SemanticDispatchError(
            f"Animation IR is invalid: {details}"
        )

    if len(scene.characters) != 1:
        raise SemanticDispatchError(
            "Phase 3C requires exactly one animated character."
        )

    timeline_end = max(
        1,
        _seconds_to_duration_frames(
            scene.duration_seconds,
            fps,
        ),
    )

    commands: list[
        BlenderActionCommand
    ] = []

    character = scene.characters[0]

    for index, animation_action in enumerate(
        character.actions
    ):
        start_frame = _seconds_to_start_frame(
            animation_action.start_seconds,
            fps,
        )

        duration_frames = (
            _seconds_to_duration_frames(
                animation_action.duration_seconds,
                fps,
            )
        )

        if animation_action.action == "idle":
            minimum_frames = 12

            command = BlenderActionCommand(
                action="idle",
                start_frame=start_frame,
                duration_frames=duration_frames,
            )

        elif animation_action.action == "turn_head":
            minimum_frames = 6

            command = BlenderActionCommand(
                action="turn_head",
                start_frame=start_frame,
                duration_frames=duration_frames,
                direction="right",
            )

        elif animation_action.action == "wave":
            minimum_frames = 8

            command = BlenderActionCommand(
                action="wave",
                start_frame=start_frame,
                duration_frames=duration_frames,
                side="L",
            )

        elif animation_action.action == "step_forward":
            minimum_frames = 8

            command = BlenderActionCommand(
                action="step_forward",
                start_frame=start_frame,
                duration_frames=duration_frames,
                distance=0.75,
            )

        else:
            raise SemanticDispatchError(
                "Unsupported semantic action "
                f"'{animation_action.action}' "
                f"at actions[{index}]."
            )

        if duration_frames < minimum_frames:
            raise SemanticDispatchError(
                f"Action '{animation_action.action}' requires "
                f"at least {minimum_frames} frames but received "
                f"{duration_frames}."
            )

        if command.end_frame > timeline_end:
            raise SemanticDispatchError(
                f"Action '{animation_action.action}' exceeds "
                "the compiled Blender timeline."
            )

        commands.append(
            command
        )

    return tuple(commands)


def execute_animation_scene(
    scene: AnimationScene,
    *,
    armature_name: str,
    fps: int = 24,
    action_functions: BlenderActionFunctions | None = None,
) -> tuple[BlenderActionCommand, ...]:
    """Execute trusted semantic commands against a Blender armature."""

    if not armature_name.strip():
        raise SemanticDispatchError(
            "Armature name must not be empty."
        )

    commands = compile_animation_scene(
        scene,
        fps=fps,
    )

    if action_functions is None:
        from .actions import (
            idle,
            step_forward,
            turn_head,
            wave,
        )

        action_functions = BlenderActionFunctions(
            idle=idle,
            turn_head=turn_head,
            wave=wave,
            step_forward=step_forward,
        )

    for command in commands:
        if command.action == "idle":
            action_functions.idle(
                armature_name=armature_name,
                start_frame=command.start_frame,
                duration_frames=command.duration_frames,
            )

        elif command.action == "turn_head":
            action_functions.turn_head(
                armature_name=armature_name,
                start_frame=command.start_frame,
                duration_frames=command.duration_frames,
                direction=command.direction,
            )

        elif command.action == "wave":
            action_functions.wave(
                armature_name=armature_name,
                start_frame=command.start_frame,
                duration_frames=command.duration_frames,
                side=command.side,
            )

        elif command.action == "step_forward":
            action_functions.step_forward(
                armature_name=armature_name,
                start_frame=command.start_frame,
                duration_frames=command.duration_frames,
                distance=command.distance,
            )

        else:
            raise SemanticDispatchError(
                f"Command action '{command.action}' is unsupported."
            )

    return commands
