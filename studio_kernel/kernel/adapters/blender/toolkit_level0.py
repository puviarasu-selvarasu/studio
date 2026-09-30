"""Deterministic Blender Animation Toolkit Level 0.

This module executes inside Blender.

It contains trusted Studio-owned primitives only. Higher layers may select
supported operations and validated values, but they must not inject Python
source code into Blender.
"""

from __future__ import annotations

from collections.abc import Iterable

import bpy
from mathutils import Vector


Vector3 = tuple[float, float, float]


class BlenderToolkitError(RuntimeError):
    """Raised when a deterministic toolkit operation cannot be completed."""


def require_object(name: str) -> bpy.types.Object:
    """Return a Blender object by exact name or fail explicitly."""

    obj = bpy.data.objects.get(name)

    if obj is None:
        raise BlenderToolkitError(
            f"Blender object does not exist: {name}"
        )

    return obj


def set_location(
    object_name: str,
    location: Vector3,
) -> None:
    """Set an object's world-space location."""

    obj = require_object(object_name)
    obj.location = location


def set_rotation_degrees(
    object_name: str,
    rotation_degrees: Vector3,
) -> None:
    """Set XYZ Euler rotation using human-readable degrees."""

    from math import radians

    obj = require_object(object_name)

    obj.rotation_euler = tuple(
        radians(value)
        for value in rotation_degrees
    )


def set_scale(
    object_name: str,
    scale: Vector3,
) -> None:
    """Set an object's XYZ scale."""

    obj = require_object(object_name)
    obj.scale = scale


def insert_transform_keyframe(
    object_name: str,
    frame: int,
    *,
    channels: Iterable[str] = (
        "location",
        "rotation_euler",
        "scale",
    ),
) -> None:
    """Insert selected transform keyframes at one frame."""

    if frame < 1:
        raise BlenderToolkitError(
            "Animation frame must be greater than or equal to 1."
        )

    obj = require_object(object_name)

    supported = {
        "location",
        "rotation_euler",
        "scale",
    }

    requested = tuple(channels)
    unsupported = set(requested) - supported

    if unsupported:
        names = ", ".join(sorted(unsupported))
        raise BlenderToolkitError(
            f"Unsupported transform channel(s): {names}"
        )

    for channel in requested:
        obj.keyframe_insert(
            data_path=channel,
            frame=frame,
        )


def configure_timeline(
    *,
    start_frame: int,
    end_frame: int,
    fps: int,
) -> None:
    """Configure deterministic scene timing."""

    if start_frame < 1:
        raise BlenderToolkitError(
            "Start frame must be greater than or equal to 1."
        )

    if end_frame < start_frame:
        raise BlenderToolkitError(
            "End frame cannot be before start frame."
        )

    if fps <= 0:
        raise BlenderToolkitError(
            "FPS must be greater than zero."
        )

    scene = bpy.context.scene
    scene.frame_start = start_frame
    scene.frame_end = end_frame
    scene.render.fps = fps


def point_camera_at(
    camera_name: str,
    target: Vector3,
) -> None:
    """Orient a camera toward a world-space target."""

    camera = require_object(camera_name)

    if camera.type != "CAMERA":
        raise BlenderToolkitError(
            f"Object is not a camera: {camera_name}"
        )

    direction = Vector(target) - camera.location

    if direction.length == 0:
        raise BlenderToolkitError(
            "Camera and target cannot occupy the same position."
        )

    camera.rotation_euler = (
        direction.to_track_quat("-Z", "Y").to_euler()
    )