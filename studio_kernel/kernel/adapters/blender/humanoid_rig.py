"""Deterministic Blender builder for Studio's canonical humanoid rig.

This trusted module executes inside Blender. It constructs only the
Studio-owned canonical armature and does not execute dynamic Python.
"""

from __future__ import annotations

import bpy

from .rig_contract import HUMANOID_RIG


class HumanoidRigError(RuntimeError):
    """Raised when the canonical humanoid rig cannot be constructed."""


_BONE_GEOMETRY = {
    "root": ((0.0, 0.0, 0.0), (0.0, 0.0, 0.35)),
    "pelvis": ((0.0, 0.0, 0.35), (0.0, 0.0, 1.0)),
    "spine": ((0.0, 0.0, 1.0), (0.0, 0.0, 1.65)),
    "chest": ((0.0, 0.0, 1.65), (0.0, 0.0, 2.25)),
    "neck": ((0.0, 0.0, 2.25), (0.0, 0.0, 2.55)),
    "head": ((0.0, 0.0, 2.55), (0.0, 0.0, 3.15)),
    "upper_arm.L": (
        (0.0, 0.0, 2.15),
        (0.75, 0.0, 2.15),
    ),
    "forearm.L": (
        (0.75, 0.0, 2.15),
        (1.45, 0.0, 2.15),
    ),
    "hand.L": (
        (1.45, 0.0, 2.15),
        (1.85, 0.0, 2.15),
    ),
    "upper_arm.R": (
        (0.0, 0.0, 2.15),
        (-0.75, 0.0, 2.15),
    ),
    "forearm.R": (
        (-0.75, 0.0, 2.15),
        (-1.45, 0.0, 2.15),
    ),
    "hand.R": (
        (-1.45, 0.0, 2.15),
        (-1.85, 0.0, 2.15),
    ),
    "thigh.L": (
        (0.35, 0.0, 0.75),
        (0.35, 0.0, -0.35),
    ),
    "shin.L": (
        (0.35, 0.0, -0.35),
        (0.35, 0.0, -1.35),
    ),
    "foot.L": (
        (0.35, 0.0, -1.35),
        (0.35, -0.55, -1.35),
    ),
    "thigh.R": (
        (-0.35, 0.0, 0.75),
        (-0.35, 0.0, -0.35),
    ),
    "shin.R": (
        (-0.35, 0.0, -0.35),
        (-0.35, 0.0, -1.35),
    ),
    "foot.R": (
        (-0.35, 0.0, -1.35),
        (-0.35, -0.55, -1.35),
    ),
}


def create_humanoid_armature(
    object_name: str = "StudioHumanoidRig",
) -> bpy.types.Object:
    """Create Studio's deterministic canonical humanoid armature."""

    if not object_name.strip():
        raise HumanoidRigError(
            "Armature object name must not be empty."
        )

    if bpy.data.objects.get(object_name) is not None:
        raise HumanoidRigError(
            f"Blender object already exists: {object_name}"
        )

    armature_data = bpy.data.armatures.new(
        f"{object_name}Data"
    )

    armature_object = bpy.data.objects.new(
        object_name,
        armature_data,
    )

    bpy.context.scene.collection.objects.link(
        armature_object
    )

    bpy.context.view_layer.objects.active = armature_object
    armature_object.select_set(True)

    try:
        bpy.ops.object.mode_set(mode="EDIT")

        created = {}

        for definition in HUMANOID_RIG:
            geometry = _BONE_GEOMETRY.get(
                definition.name
            )

            if geometry is None:
                raise HumanoidRigError(
                    "Missing geometry for canonical bone: "
                    f"{definition.name}"
                )

            bone = armature_data.edit_bones.new(
                definition.name
            )

            bone.head = geometry[0]
            bone.tail = geometry[1]

            if definition.parent is not None:
                parent = created.get(
                    definition.parent
                )

                if parent is None:
                    raise HumanoidRigError(
                        "Parent bone was not created before "
                        f"child: {definition.name}"
                    )

                bone.parent = parent

            created[definition.name] = bone

        bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        if armature_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        bpy.data.objects.remove(
            armature_object,
            do_unlink=True,
        )

        bpy.data.armatures.remove(
            armature_data,
        )

        raise

    armature_object.show_in_front = True

    return armature_object
