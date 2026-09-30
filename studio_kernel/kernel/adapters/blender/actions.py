"""Trusted deterministic Level-1 animation actions for Studio.

Semantic actions translate bounded animation intent into trusted pose-control
operations. They do not execute dynamic Python or communicate externally.
"""

from __future__ import annotations

from .pose_controls import (
    insert_bone_rotation_keyframe,
    set_bone_rotation_degrees,
)
from .toolkit_level0 import (
    get_location,
    insert_transform_keyframe,
    set_location,
)


class AnimationActionError(ValueError):
    """Raised when a semantic animation action is invalid."""


def wave(
    armature_name: str,
    start_frame: int,
    duration_frames: int,
    side: str = "L",
) -> None:
    """Create one deterministic arm wave using trusted pose controls."""

    if not armature_name.strip():
        raise AnimationActionError(
            "Armature name must not be empty."
        )

    if start_frame < 1:
        raise AnimationActionError(
            "Start frame must be greater than or equal to 1."
        )

    if duration_frames < 8:
        raise AnimationActionError(
            "Wave duration must be at least 8 frames."
        )

    normalized_side = side.upper()

    if normalized_side not in {"L", "R"}:
        raise AnimationActionError(
            "Wave side must be 'L' or 'R'."
        )

    upper_arm = f"upper_arm.{normalized_side}"
    forearm = f"forearm.{normalized_side}"

    direction = 1.0 if normalized_side == "L" else -1.0

    end_frame = start_frame + duration_frames

    quarter = duration_frames // 4

    pose_frames = (
        start_frame,
        start_frame + quarter,
        start_frame + (quarter * 2),
        start_frame + (quarter * 3),
        end_frame,
    )

    upper_arm_poses = (
        (0.0, 0.0, 0.0),
        (35.0, 0.0, 25.0 * direction),
        (35.0, 0.0, 25.0 * direction),
        (35.0, 0.0, 25.0 * direction),
        (0.0, 0.0, 0.0),
    )

    forearm_poses = (
        (0.0, 0.0, 0.0),
        (0.0, -70.0 * direction, 0.0),
        (0.0, -105.0 * direction, 0.0),
        (0.0, -55.0 * direction, 0.0),
        (0.0, 0.0, 0.0),
    )

    for frame, upper_rotation, forearm_rotation in zip(
        pose_frames,
        upper_arm_poses,
        forearm_poses,
        strict=True,
    ):
        set_bone_rotation_degrees(
            armature_name,
            upper_arm,
            upper_rotation,
        )

        insert_bone_rotation_keyframe(
            armature_name,
            upper_arm,
            frame,
        )

        set_bone_rotation_degrees(
            armature_name,
            forearm,
            forearm_rotation,
        )

        insert_bone_rotation_keyframe(
            armature_name,
            forearm,
            frame,
        )


def turn_head(
    armature_name: str,
    start_frame: int,
    duration_frames: int,
    direction: str,
) -> None:
    """Turn the head left or right, hold briefly, then return neutral."""

    if not armature_name.strip():
        raise AnimationActionError(
            "Armature name must not be empty."
        )

    if start_frame < 1:
        raise AnimationActionError(
            "Start frame must be greater than or equal to 1."
        )

    if duration_frames < 6:
        raise AnimationActionError(
            "Head-turn duration must be at least 6 frames."
        )

    normalized_direction = direction.lower()

    if normalized_direction not in {"left", "right"}:
        raise AnimationActionError(
            "Head-turn direction must be 'left' or 'right'."
        )

    direction_sign = (
        1.0
        if normalized_direction == "left"
        else -1.0
    )

    end_frame = start_frame + duration_frames

    turn_frame = (
        start_frame
        + max(1, duration_frames // 3)
    )

    hold_frame = (
        start_frame
        + max(2, (duration_frames * 2) // 3)
    )

    poses = (
        (
            start_frame,
            (0.0, 0.0, 0.0),
        ),
        (
            turn_frame,
            (0.0, 0.0, 30.0 * direction_sign),
        ),
        (
            hold_frame,
            (0.0, 0.0, 30.0 * direction_sign),
        ),
        (
            end_frame,
            (0.0, 0.0, 0.0),
        ),
    )

    for frame, rotation in poses:
        set_bone_rotation_degrees(
            armature_name,
            "head",
            rotation,
        )

        insert_bone_rotation_keyframe(
            armature_name,
            "head",
            frame,
        )


def idle(
    armature_name: str,
    start_frame: int,
    duration_frames: int,
) -> None:
    """Create a sparse limited-animation breathing idle."""

    if not armature_name.strip():
        raise AnimationActionError(
            "Armature name must not be empty."
        )

    if start_frame < 1:
        raise AnimationActionError(
            "Start frame must be greater than or equal to 1."
        )

    if duration_frames < 12:
        raise AnimationActionError(
            "Idle duration must be at least 12 frames."
        )

    end_frame = start_frame + duration_frames
    midpoint = start_frame + (duration_frames // 2)

    poses = (
        (
            start_frame,
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
        ),
        (
            midpoint,
            (2.0, 0.0, 0.0),
            (-1.0, 0.0, 0.0),
        ),
        (
            end_frame,
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0),
        ),
    )

    for frame, chest_rotation, head_rotation in poses:
        set_bone_rotation_degrees(
            armature_name,
            "chest",
            chest_rotation,
        )

        insert_bone_rotation_keyframe(
            armature_name,
            "chest",
            frame,
        )

        set_bone_rotation_degrees(
            armature_name,
            "head",
            head_rotation,
        )

        insert_bone_rotation_keyframe(
            armature_name,
            "head",
            frame,
        )

def step_forward(
    armature_name: str,
    start_frame: int,
    duration_frames: int,
    distance: float = 0.75,
) -> None:
    """Create one bounded forward step with sparse body motion."""

    if not armature_name.strip():
        raise AnimationActionError(
            "Armature name must not be empty."
        )

    if start_frame < 1:
        raise AnimationActionError(
            "Start frame must be greater than or equal to 1."
        )

    if duration_frames < 8:
        raise AnimationActionError(
            "Step duration must be at least 8 frames."
        )

    if distance <= 0.0 or distance > 2.0:
        raise AnimationActionError(
            "Step distance must be greater than 0 and at most 2."
        )

    end_frame = start_frame + duration_frames
    midpoint = start_frame + (duration_frames // 2)

    start_location = get_location(
        armature_name
    )

    set_location(
        armature_name,
        start_location,
    )

    insert_transform_keyframe(
        armature_name,
        start_frame,
        channels=("location",),
    )

    for bone_name in (
        "thigh.L",
        "thigh.R",
    ):
        set_bone_rotation_degrees(
            armature_name,
            bone_name,
            (0.0, 0.0, 0.0),
        )
        insert_bone_rotation_keyframe(
            armature_name,
            bone_name,
            start_frame,
        )

    set_bone_rotation_degrees(
        armature_name,
        "thigh.L",
        (-20.0, 0.0, 0.0),
    )

    set_bone_rotation_degrees(
        armature_name,
        "thigh.R",
        (20.0, 0.0, 0.0),
    )

    insert_bone_rotation_keyframe(
        armature_name,
        "thigh.L",
        midpoint,
    )

    insert_bone_rotation_keyframe(
        armature_name,
        "thigh.R",
        midpoint,
    )

    set_location(
        armature_name,
        (
            start_location[0],
            start_location[1] - distance,
            start_location[2],
        ),
    )

    insert_transform_keyframe(
        armature_name,
        end_frame,
        channels=("location",),
    )

    for bone_name in (
        "thigh.L",
        "thigh.R",
    ):
        set_bone_rotation_degrees(
            armature_name,
            bone_name,
            (0.0, 0.0, 0.0),
        )

        insert_bone_rotation_keyframe(
            armature_name,
            bone_name,
            end_frame,
        )
