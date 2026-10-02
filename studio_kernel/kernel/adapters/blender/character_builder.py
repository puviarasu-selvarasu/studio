"""Trusted deterministic Blender builder for Studio production characters."""

from __future__ import annotations

from dataclasses import dataclass

import bpy

from kernel.adapters.blender.deterministic_shot import (
    parent_object_to_bone,
)
from kernel.adapters.blender.humanoid_rig import (
    create_humanoid_armature,
)
from kernel.characters.production import (
    BodyProfile,
    CharacterPaletteProfile,
    CharacterProductionSpec,
    HairProfile,
    OutfitProfile,
    RigProfile,
)


class CharacterBuilderError(RuntimeError):
    """Represent deterministic production-character construction failure."""


@dataclass(
    frozen=True,
    slots=True,
)
class BuiltCharacter:
    """Hold trusted Blender objects created for one production character."""

    armature: bpy.types.Object
    body_parts: tuple[bpy.types.Object, ...]
    face_parts: tuple[bpy.types.Object, ...]
    hair_parts: tuple[bpy.types.Object, ...]
    outfit_parts: tuple[bpy.types.Object, ...]

    @property
    def render_parts(
        self,
    ) -> tuple[bpy.types.Object, ...]:
        """Return all visible character meshes in stable construction order."""

        return (
            self.body_parts
            + self.face_parts
            + self.hair_parts
            + self.outfit_parts
        )


_MOMO_SKIN = (
    0.72,
    0.52,
    0.40,
    1.0,
)

_MOMO_HAIR = (
    0.045,
    0.035,
    0.050,
    1.0,
)

_MOMO_FACE = (
    0.020,
    0.025,
    0.035,
    1.0,
)

_MOMO_OUTFIT = (
    0.16,
    0.20,
    0.30,
    1.0,
)

_MOMO_OUTFIT_ACCENT = (
    0.58,
    0.08,
    0.10,
    1.0,
)


def _validate_supported_spec(
    spec: CharacterProductionSpec,
) -> None:
    """Reject production profiles this trusted builder does not implement."""

    if not isinstance(
        spec,
        CharacterProductionSpec,
    ):
        raise CharacterBuilderError(
            "spec must be CharacterProductionSpec."
        )

    expected = (
        (
            spec.rig_profile,
            RigProfile.STUDIO_HUMANOID_V1,
            "rig",
        ),
        (
            spec.body_profile,
            BodyProfile.LIGHTWEIGHT_ANIME_V1,
            "body",
        ),
        (
            spec.hair_profile,
            HairProfile.SHOULDER_LENGTH_DARK_V1,
            "hair",
        ),
        (
            spec.outfit_profile,
            OutfitProfile.SIMPLE_EVERYDAY_V1,
            "outfit",
        ),
        (
            spec.palette_profile,
            CharacterPaletteProfile.MOMO_DEFAULT_V1,
            "palette",
        ),
    )

    for actual, supported, label in expected:
        if actual is not supported:
            raise CharacterBuilderError(
                f"Unsupported {label} production profile: {actual}"
            )


def _prefix(
    spec: CharacterProductionSpec,
) -> str:
    """Return a deterministic Blender-safe object prefix."""

    return (
        "StudioCharacter_"
        + spec.character_id
        + "_"
        + spec.variant_id
    )


def _material(
    name: str,
    rgba: tuple[
        float,
        float,
        float,
        float,
    ],
) -> bpy.types.Material:
    """Create one lightweight Workbench-compatible material."""

    material = bpy.data.materials.new(
        name=name
    )

    material.diffuse_color = rgba

    return material


def _assign_material(
    obj: bpy.types.Object,
    material: bpy.types.Material,
) -> None:
    """Assign exactly one material to one mesh object."""

    if obj.type != "MESH":
        raise CharacterBuilderError(
            f"Material target is not a mesh: {obj.name}"
        )

    obj.data.materials.clear()
    obj.data.materials.append(
        material
    )


def _require_bone(
    rig: bpy.types.Object,
    bone_name: str,
):
    """Return one canonical rig bone or fail explicitly."""

    bone = rig.data.bones.get(
        bone_name
    )

    if bone is None:
        raise CharacterBuilderError(
            f"Required character bone missing: {bone_name}"
        )

    return bone


def _apply_anime_neutral_pose(
    rig: bpy.types.Object,
) -> None:
    """Lower canonical horizontal arms into a relaxed production pose."""

    rotations = {
        "upper_arm.L": -0.92,
        "upper_arm.R": -0.92,
    }

    for bone_name, x_rotation in rotations.items():
        pose_bone = rig.pose.bones.get(
            bone_name
        )

        if pose_bone is None:
            raise CharacterBuilderError(
                "Required neutral-pose bone missing: "
                + bone_name
            )

        pose_bone.rotation_mode = "XYZ"

        pose_bone.rotation_euler[0] = (
            x_rotation
        )

    bpy.context.view_layer.update()


def _create_segment(
    *,
    rig: bpy.types.Object,
    prefix: str,
    bone_name: str,
    width: float,
    depth: float,
    length_scale: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create one deterministic lightweight body segment."""

    bone = _require_bone(
        rig,
        bone_name,
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    direction = (
        bone.tail_local
        - bone.head_local
    )

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=midpoint,
    )

    obj = bpy.context.active_object

    if obj is None:
        raise CharacterBuilderError(
            f"Unable to create character segment: {bone_name}"
        )

    obj.name = (
        prefix
        + "_Body_"
        + bone_name.replace(
            ".",
            "_",
        )
    )

    obj.dimensions = (
        width,
        depth,
        max(
            bone.length
            * length_scale,
            0.08,
        ),
    )

    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (
        direction.to_track_quat(
            "Z",
            "Y",
        )
    )

    bpy.context.view_layer.objects.active = obj

    obj.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    obj.select_set(
        False
    )

    _assign_material(
        obj,
        material,
    )

    parent_object_to_bone(
        obj,
        rig,
        bone_name,
    )

    return obj


def _create_head(
    *,
    rig: bpy.types.Object,
    prefix: str,
    scale: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create Momo's broader lightweight anime head silhouette."""

    bone = _require_bone(
        rig,
        "head",
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16,
        ring_count=10,
        radius=0.38,
        location=(
            midpoint.x,
            midpoint.y,
            midpoint.z
            + (0.015 * scale),
        ),
    )

    head = bpy.context.active_object

    if head is None:
        raise CharacterBuilderError(
            "Unable to create character head."
        )

    head.name = (
        prefix
        + "_Body_Head"
    )

    head.scale = (
        scale * 1.05,
        scale * 0.82,
        scale * 1.08,
    )

    bpy.context.view_layer.objects.active = head

    head.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    head.select_set(
        False
    )

    _assign_material(
        head,
        material,
    )

    parent_object_to_bone(
        head,
        rig,
        "head",
    )

    return head

def _create_hair_cap(
    *,
    rig: bpy.types.Object,
    prefix: str,
    head_scale: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create a beveled rear hair mass that leaves the face exposed."""

    bone = _require_bone(
        rig,
        "head",
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(
            midpoint.x,
            midpoint.y
            + (0.16 * head_scale),
            midpoint.z
            - (0.05 * head_scale),
        ),
    )

    hair = bpy.context.active_object

    if hair is None:
        raise CharacterBuilderError(
            "Unable to create rear hair."
        )

    hair.name = (
        prefix
        + "_Hair_Back"
    )

    hair.dimensions = (
        0.86 * head_scale,
        0.32 * head_scale,
        1.02 * head_scale,
    )

    bpy.context.view_layer.objects.active = hair

    hair.select_set(True)

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    hair.select_set(False)

    bevel = hair.modifiers.new(
        name="StudioHairBackBevel",
        type="BEVEL",
    )

    bevel.width = (
        0.09
        * head_scale
    )

    bevel.segments = 2

    _assign_material(
        hair,
        material,
    )

    parent_object_to_bone(
        hair,
        rig,
        "head",
    )

    return hair

def _create_hair_top(
    *,
    rig: bpy.types.Object,
    prefix: str,
    head_scale: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create a rounded crown mass for a readable anime silhouette."""

    bone = _require_bone(
        rig,
        "head",
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=10,
        ring_count=6,
        radius=0.5,
        location=(
            midpoint.x,
            midpoint.y
            + (0.02 * head_scale),
            midpoint.z
            + (0.31 * head_scale),
        ),
    )

    hair = bpy.context.active_object

    if hair is None:
        raise CharacterBuilderError(
            "Unable to create top hair."
        )

    hair.name = (
        prefix
        + "_Hair_Top"
    )

    hair.dimensions = (
        0.88 * head_scale,
        0.46 * head_scale,
        0.36 * head_scale,
    )

    bpy.context.view_layer.objects.active = hair

    hair.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    hair.select_set(
        False
    )

    _assign_material(
        hair,
        material,
    )

    parent_object_to_bone(
        hair,
        rig,
        "head",
    )

    return hair

def _create_hair_fringe(
    *,
    rig: bpy.types.Object,
    prefix: str,
    head_scale: float,
    material: bpy.types.Material,
) -> tuple[bpy.types.Object, ...]:
    """Create three cheap angled fringe pieces across the forehead."""

    bone = _require_bone(
        rig,
        "head",
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    specs = (
        (
            "L",
            -0.22,
            -0.30,
        ),
        (
            "C",
            0.00,
            0.02,
        ),
        (
            "R",
            0.22,
            0.30,
        ),
    )

    parts = []

    for (
        label,
        x_offset,
        angle,
    ) in specs:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(
                midpoint.x
                + (
                    x_offset
                    * head_scale
                ),
                midpoint.y
                - (
                    0.31
                    * head_scale
                ),
                midpoint.z
                + (
                    0.23
                    * head_scale
                ),
            ),
        )

        fringe = bpy.context.active_object

        if fringe is None:
            raise CharacterBuilderError(
                "Unable to create hair fringe."
            )

        fringe.name = (
            prefix
            + "_Hair_Fringe_"
            + label
        )

        fringe.dimensions = (
            0.19 * head_scale,
            0.10 * head_scale,
            0.37 * head_scale,
        )

        fringe.rotation_mode = "XYZ"

        fringe.rotation_euler[1] = angle

        bpy.context.view_layer.objects.active = fringe

        fringe.select_set(
            True
        )

        bpy.ops.object.transform_apply(
            location=False,
            rotation=False,
            scale=True,
        )

        fringe.select_set(
            False
        )

        bevel = fringe.modifiers.new(
            name="StudioHairFringeBevel",
            type="BEVEL",
        )

        bevel.width = (
            0.025
            * head_scale
        )

        bevel.segments = 1

        _assign_material(
            fringe,
            material,
        )

        parent_object_to_bone(
            fringe,
            rig,
            "head",
        )

        parts.append(
            fringe
        )

    return tuple(
        parts
    )


def _create_face_mark(
    *,
    rig: bpy.types.Object,
    prefix: str,
    label: str,
    x_offset: float,
    z_offset: float,
    width: float,
    height: float,
    head_scale: float,
    material: bpy.types.Material,
    front_offset: float = 0.330,
    rounded: bool = False,
) -> bpy.types.Object:
    """Create one deterministic layered anime facial feature."""

    bone = _require_bone(
        rig,
        "head",
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    location = (
        midpoint.x
        + (
            x_offset
            * head_scale
        ),
        midpoint.y
        - (
            front_offset
            * head_scale
        ),
        midpoint.z
        + (
            z_offset
            * head_scale
        ),
    )

    if rounded:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8,
            ring_count=4,
            radius=0.5,
            location=location,
        )
    else:
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=location,
        )

    mark = bpy.context.active_object

    if mark is None:
        raise CharacterBuilderError(
            "Unable to create face mark: "
            + label
        )

    mark.name = (
        prefix
        + "_Face_"
        + label
    )

    mark.dimensions = (
        width * head_scale,
        0.032 * head_scale,
        height * head_scale,
    )

    bpy.context.view_layer.objects.active = mark

    mark.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    mark.select_set(
        False
    )

    _assign_material(
        mark,
        material,
    )

    parent_object_to_bone(
        mark,
        rig,
        "head",
    )

    return mark

def _create_hair_lock(
    *,
    rig: bpy.types.Object,
    prefix: str,
    side: str,
    head_scale: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create one rounded shoulder-length anime side lock."""

    if side not in {
        "L",
        "R",
    }:
        raise CharacterBuilderError(
            "Hair-lock side must be L or R."
        )

    bone = _require_bone(
        rig,
        "head",
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    direction = (
        -1.0
        if side == "L"
        else 1.0
    )

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8,
        ring_count=5,
        radius=0.5,
        location=(
            midpoint.x
            + (
                direction
                * 0.32
                * head_scale
            ),
            midpoint.y
            + (0.10 * head_scale),
            midpoint.z
            - (0.22 * head_scale),
        ),
    )

    lock = bpy.context.active_object

    if lock is None:
        raise CharacterBuilderError(
            "Unable to create character hair lock."
        )

    lock.name = (
        prefix
        + "_Hair_Lock_"
        + side
    )

    lock.dimensions = (
        0.19 * head_scale,
        0.19 * head_scale,
        0.78 * head_scale,
    )

    lock.rotation_mode = "XYZ"

    lock.rotation_euler[1] = (
        direction
        * 0.14
    )

    bpy.context.view_layer.objects.active = lock

    lock.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    lock.select_set(
        False
    )

    _assign_material(
        lock,
        material,
    )

    parent_object_to_bone(
        lock,
        rig,
        "head",
    )

    return lock

def _create_outfit_shell(
    *,
    rig: bpy.types.Object,
    prefix: str,
    bone_name: str,
    label: str,
    width: float,
    depth: float,
    length_scale: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create one rounded low-poly outfit layer around a canonical torso bone."""

    bone = _require_bone(
        rig,
        bone_name,
    )

    midpoint = (
        bone.head_local
        + bone.tail_local
    ) * 0.5

    direction = (
        bone.tail_local
        - bone.head_local
    )

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8,
        ring_count=5,
        radius=0.5,
        location=midpoint,
    )

    obj = bpy.context.active_object

    if obj is None:
        raise CharacterBuilderError(
            f"Unable to create outfit component: {label}"
        )

    obj.name = (
        prefix
        + "_Outfit_"
        + label
    )

    obj.dimensions = (
        width,
        depth,
        max(
            bone.length * length_scale,
            0.10,
        ),
    )

    obj.rotation_mode = "QUATERNION"

    obj.rotation_quaternion = (
        direction.to_track_quat(
            "Z",
            "Y",
        )
    )

    bpy.context.view_layer.objects.active = obj

    obj.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    obj.select_set(
        False
    )

    _assign_material(
        obj,
        material,
    )

    parent_object_to_bone(
        obj,
        rig,
        bone_name,
    )

    return obj

def build_character(
    spec: CharacterProductionSpec,
) -> BuiltCharacter:
    """Build one reusable lightweight character from a trusted production spec."""

    _validate_supported_spec(
        spec
    )

    prefix = _prefix(
        spec
    )

    rig_name = (
        prefix
        + "_Rig"
    )

    if bpy.data.objects.get(
        rig_name
    ) is not None:
        raise CharacterBuilderError(
            f"Character rig already exists: {rig_name}"
        )

    rig = create_humanoid_armature(
        rig_name
    )

    skin = _material(
        prefix + "_Material_Skin",
        _MOMO_SKIN,
    )

    hair_material = _material(
        prefix + "_Material_Hair",
        _MOMO_HAIR,
    )

    face_material = _material(
        prefix + "_Material_Face",
        _MOMO_FACE,
    )

    eye_white_material = _material(
        prefix + "_Material_EyeWhite",
        (
            0.94,
            0.95,
            0.96,
            1.0,
        ),
    )

    outfit_material = _material(
        prefix + "_Material_Outfit",
        _MOMO_OUTFIT,
    )

    accent_material = _material(
        prefix + "_Material_Accent",
        _MOMO_OUTFIT_ACCENT,
    )

    proportions = spec.proportions

    segment_specs = (
        (
            "pelvis",
            0.42 * proportions.hip_scale,
            0.30 * proportions.hip_scale,
            0.86,
        ),
        (
            "spine",
            0.39 * proportions.torso_scale,
            0.28 * proportions.torso_scale,
            0.86,
        ),
        (
            "chest",
            0.50 * proportions.shoulder_scale,
            0.32 * proportions.torso_scale,
            0.88,
        ),
        (
            "neck",
            0.18,
            0.17,
            0.80,
        ),
        (
            "upper_arm.L",
            0.18 * proportions.limb_scale,
            0.18 * proportions.limb_scale,
            0.86,
        ),
        (
            "forearm.L",
            0.15 * proportions.limb_scale,
            0.15 * proportions.limb_scale,
            0.86,
        ),
        (
            "hand.L",
            0.17 * proportions.limb_scale,
            0.12 * proportions.limb_scale,
            0.82,
        ),
        (
            "upper_arm.R",
            0.18 * proportions.limb_scale,
            0.18 * proportions.limb_scale,
            0.86,
        ),
        (
            "forearm.R",
            0.15 * proportions.limb_scale,
            0.15 * proportions.limb_scale,
            0.86,
        ),
        (
            "hand.R",
            0.17 * proportions.limb_scale,
            0.12 * proportions.limb_scale,
            0.82,
        ),
        (
            "thigh.L",
            0.22 * proportions.limb_scale,
            0.22 * proportions.limb_scale,
            0.90,
        ),
        (
            "shin.L",
            0.17 * proportions.limb_scale,
            0.17 * proportions.limb_scale,
            0.90,
        ),
        (
            "foot.L",
            0.20 * proportions.limb_scale,
            0.28 * proportions.limb_scale,
            0.80,
        ),
        (
            "thigh.R",
            0.22 * proportions.limb_scale,
            0.22 * proportions.limb_scale,
            0.90,
        ),
        (
            "shin.R",
            0.17 * proportions.limb_scale,
            0.17 * proportions.limb_scale,
            0.90,
        ),
        (
            "foot.R",
            0.20 * proportions.limb_scale,
            0.28 * proportions.limb_scale,
            0.80,
        ),
    )

    body_parts = tuple(
        _create_segment(
            rig=rig,
            prefix=prefix,
            bone_name=bone_name,
            width=width,
            depth=depth,
            length_scale=length_scale,
            material=skin,
        )
        for (
            bone_name,
            width,
            depth,
            length_scale,
        ) in segment_specs
    )

    head = _create_head(
        rig=rig,
        prefix=prefix,
        scale=proportions.head_scale,
        material=skin,
    )

    body_parts = (
        body_parts
        + (
            head,
        )
    )

    face_parts = (
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Eye_L",
            x_offset=-0.15,
            z_offset=0.07,
            width=0.19,
            height=0.105,
            head_scale=proportions.head_scale,
            material=eye_white_material,
            front_offset=0.330,
            rounded=True,
        ),
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Eye_R",
            x_offset=0.15,
            z_offset=0.07,
            width=0.19,
            height=0.105,
            head_scale=proportions.head_scale,
            material=eye_white_material,
            front_offset=0.330,
            rounded=True,
        ),
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Pupil_L",
            x_offset=-0.15,
            z_offset=0.065,
            width=0.064,
            height=0.082,
            head_scale=proportions.head_scale,
            material=face_material,
            front_offset=0.342,
            rounded=True,
        ),
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Pupil_R",
            x_offset=0.15,
            z_offset=0.065,
            width=0.064,
            height=0.082,
            head_scale=proportions.head_scale,
            material=face_material,
            front_offset=0.342,
            rounded=True,
        ),
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Brow_L",
            x_offset=-0.15,
            z_offset=0.18,
            width=0.16,
            height=0.020,
            head_scale=proportions.head_scale,
            material=face_material,
            front_offset=0.338,
        ),
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Brow_R",
            x_offset=0.15,
            z_offset=0.18,
            width=0.16,
            height=0.020,
            head_scale=proportions.head_scale,
            material=face_material,
            front_offset=0.338,
        ),
        _create_face_mark(
            rig=rig,
            prefix=prefix,
            label="Mouth",
            x_offset=0.0,
            z_offset=-0.13,
            width=0.12,
            height=0.018,
            head_scale=proportions.head_scale,
            material=face_material,
            front_offset=0.338,
        ),
    )

    hair_parts = (
        _create_hair_cap(
            rig=rig,
            prefix=prefix,
            head_scale=proportions.head_scale,
            material=hair_material,
        ),
        _create_hair_top(
            rig=rig,
            prefix=prefix,
            head_scale=proportions.head_scale,
            material=hair_material,
        ),
        _create_hair_lock(
            rig=rig,
            prefix=prefix,
            side="L",
            head_scale=proportions.head_scale,
            material=hair_material,
        ),
        _create_hair_lock(
            rig=rig,
            prefix=prefix,
            side="R",
            head_scale=proportions.head_scale,
            material=hair_material,
        ),
        *_create_hair_fringe(
            rig=rig,
            prefix=prefix,
            head_scale=proportions.head_scale,
            material=hair_material,
        ),
    )

    outfit_parts = (
        _create_outfit_shell(
            rig=rig,
            prefix=prefix,
            bone_name="chest",
            label="Top",
            width=(
                0.58
                * proportions.shoulder_scale
            ),
            depth=(
                0.38
                * proportions.torso_scale
            ),
            length_scale=1.00,
            material=outfit_material,
        ),
        _create_outfit_shell(
            rig=rig,
            prefix=prefix,
            bone_name="spine",
            label="Mid",
            width=(
                0.49
                * proportions.torso_scale
            ),
            depth=(
                0.34
                * proportions.torso_scale
            ),
            length_scale=1.05,
            material=outfit_material,
        ),
        _create_outfit_shell(
            rig=rig,
            prefix=prefix,
            bone_name="pelvis",
            label="Lower",
            width=(
                0.50
                * proportions.hip_scale
            ),
            depth=(
                0.40
                * proportions.hip_scale
            ),
            length_scale=1.00,
            material=outfit_material,
        ),
        _create_outfit_shell(
            rig=rig,
            prefix=prefix,
            bone_name="neck",
            label="Accent",
            width=0.24,
            depth=0.20,
            length_scale=0.48,
            material=accent_material,
        ),
    )

    _apply_anime_neutral_pose(
        rig
    )

    bpy.context.view_layer.update()

    return BuiltCharacter(
        armature=rig,
        body_parts=body_parts,
        face_parts=face_parts,
        hair_parts=hair_parts,
        outfit_parts=outfit_parts,
    )
