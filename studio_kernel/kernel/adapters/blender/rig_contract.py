"""Canonical rig contract for Studio-controlled humanoid characters.

This module deliberately has no Blender dependency. It defines the stable
bone vocabulary that trusted Blender infrastructure must implement.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RigBone:
    """Describe one canonical Studio humanoid bone."""

    name: str
    parent: str | None


HUMANOID_RIG = (
    RigBone("root", None),
    RigBone("pelvis", "root"),
    RigBone("spine", "pelvis"),
    RigBone("chest", "spine"),
    RigBone("neck", "chest"),
    RigBone("head", "neck"),
    RigBone("upper_arm.L", "chest"),
    RigBone("forearm.L", "upper_arm.L"),
    RigBone("hand.L", "forearm.L"),
    RigBone("upper_arm.R", "chest"),
    RigBone("forearm.R", "upper_arm.R"),
    RigBone("hand.R", "forearm.R"),
    RigBone("thigh.L", "pelvis"),
    RigBone("shin.L", "thigh.L"),
    RigBone("foot.L", "shin.L"),
    RigBone("thigh.R", "pelvis"),
    RigBone("shin.R", "thigh.R"),
    RigBone("foot.R", "shin.R"),
)

HUMANOID_BONE_NAMES = tuple(
    bone.name
    for bone in HUMANOID_RIG
)


class RigContractError(ValueError):
    """Raised when a rig violates Studio's canonical contract."""


def validate_rig_bones(
    bone_names: tuple[str, ...],
) -> None:
    """Require exactly the canonical Studio humanoid bone set."""

    supplied = set(bone_names)
    required = set(HUMANOID_BONE_NAMES)

    missing = required - supplied
    unexpected = supplied - required

    if len(bone_names) != len(supplied):
        raise RigContractError(
            "Rig contains duplicate bone names."
        )

    if missing:
        names = ", ".join(sorted(missing))
        raise RigContractError(
            f"Rig is missing required bone(s): {names}"
        )

    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise RigContractError(
            f"Rig contains unexpected bone(s): {names}"
        )
