"""Trusted deterministic pose controls for Studio Blender rigs.

Higher layers may select validated bone names, rotations, and frames.
They must not inject executable Python into Blender.
"""

from __future__ import annotations

from math import radians

import bpy


Vector3 = tuple[float, float, float]


class PoseControlError(RuntimeError):
    """Raised when a deterministic pose operation cannot be completed."""


def require_armature(
    object_name: str,
) -> bpy.types.Object:
    """Return an armature object by exact name or fail explicitly."""

    obj = bpy.data.objects.get(object_name)

    if obj is None:
        raise PoseControlError(
            f"Blender object does not exist: {object_name}"
        )

    if obj.type != "ARMATURE":
        raise PoseControlError(
            f"Object is not an armature: {object_name}"
        )

    return obj


def require_pose_bone(
    armature_name: str,
    bone_name: str,
) -> bpy.types.PoseBone:
    """Return an exact pose bone from a known armature."""

    armature = require_armature(
        armature_name
    )

    bone = armature.pose.bones.get(
        bone_name
    )

    if bone is None:
        raise PoseControlError(
            f"Pose bone does not exist: {bone_name}"
        )

    return bone


def set_bone_rotation_degrees(
    armature_name: str,
    bone_name: str,
    rotation_degrees: Vector3,
) -> None:
    """Set a pose bone's XYZ Euler rotation in degrees."""

    bone = require_pose_bone(
        armature_name,
        bone_name,
    )

    bone.rotation_mode = "XYZ"

    bone.rotation_euler = tuple(
        radians(value)
        for value in rotation_degrees
    )


def insert_bone_rotation_keyframe(
    armature_name: str,
    bone_name: str,
    frame: int,
) -> None:
    """Insert one deterministic pose-bone rotation keyframe."""

    if frame < 1:
        raise PoseControlError(
            "Animation frame must be greater than or equal to 1."
        )

    bone = require_pose_bone(
        armature_name,
        bone_name,
    )

    bone.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
    )
