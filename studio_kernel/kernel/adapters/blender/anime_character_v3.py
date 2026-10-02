"""Low-cost human-anime visual refinement for Studio production characters."""

from __future__ import annotations

import bpy

from mathutils import Vector

from kernel.adapters.blender.character_builder import (
    BuiltCharacter,
)


class AnimeCharacterV3Error(
    RuntimeError
):
    """Raised when the canonical production character cannot be refined."""


def apply_human_anime_character_v3(
    built_character: BuiltCharacter,
) -> tuple[
    bpy.types.Object,
    ...,
]:
    """Refine the canonical character without replacing its identity or rig."""

    face = _face_parts(
        built_character
    )

    head = _head_object(
        built_character
    )

    if head.type != "MESH":
        raise AnimeCharacterV3Error(
            "Canonical head must be a mesh."
        )

    _smooth_mesh(
        head
    )

    # Slightly taller and less spherical while keeping all existing
    # rig/identity relationships intact.
    head.scale[
        0
    ] *= 0.955

    head.scale[
        1
    ] *= 0.965

    head.scale[
        2
    ] *= 1.035

    bpy.context.view_layer.update()

    for hair in (
        built_character.hair_parts
    ):
        _smooth_mesh(
            hair
        )

        lowered = (
            hair.name.lower()
        )

        # The old rectangular forehead slabs are replaced below
        # by pointed anime fringe geometry.
        if (
            "fringe" in lowered
            or "lock" in lowered
        ):
            hair.hide_render = True
            hair.hide_viewport = True

    # Replace mechanical face marks with shaped production meshes.
    _replace_with_almond(
        face[
            "Eye_L"
        ],
        width_scale=1.20,
        height_scale=0.88,
    )

    _replace_with_almond(
        face[
            "Eye_R"
        ],
        width_scale=1.20,
        height_scale=0.88,
    )

    _replace_with_ellipse(
        face[
            "Pupil_L"
        ],
        width_scale=0.84,
        height_scale=1.08,
        point_count=12,
    )

    _replace_with_ellipse(
        face[
            "Pupil_R"
        ],
        width_scale=0.84,
        height_scale=1.08,
        point_count=12,
    )

    _replace_with_tapered_brow(
        face[
            "Brow_L"
        ],
        mirror=False,
    )

    _replace_with_tapered_brow(
        face[
            "Brow_R"
        ],
        mirror=True,
    )

    _replace_with_mouth_shape(
        face[
            "Mouth"
        ]
    )

    ink = _material(
        "_Material_AnimeV3_Ink",
        (
            0.018,
            0.024,
            0.030,
            1.0,
        ),
    )

    skin = _first_material(
        head
    )

    if skin is None:
        skin = _material(
            "_Material_AnimeV3_Skin",
            (
                0.76,
                0.66,
                0.57,
                1.0,
            ),
        )

    nose_shadow = _material(
        "_Material_AnimeV3_NoseShadow",
        (
            0.46,
            0.35,
            0.31,
            1.0,
        ),
    )

    hair_material = None

    for item in (
        built_character.hair_parts
    ):
        hair_material = (
            _first_material(
                item
            )
        )

        if hair_material is not None:
            break

    if hair_material is None:
        hair_material = _material(
            "_Material_AnimeV3_Hair",
            (
                0.055,
                0.042,
                0.075,
                1.0,
            ),
        )

    head_center = (
        head.matrix_world.translation.copy()
    )

    half_width = (
        head.dimensions.x
        * 0.5
    )

    half_depth = (
        head.dimensions.y
        * 0.5
    )

    half_height = (
        head.dimensions.z
        * 0.5
    )

    front_y = (
        head_center.y
        - half_depth
        - 0.018
    )

    created: list[
        bpy.types.Object
    ] = []

    # Small ears establish a more human head silhouette.
    created.append(
        _create_flat_ellipse(
            name=(
                built_character.armature.name
                .removesuffix(
                    "_Rig"
                )
                + "_AnimeV3_Ear_L"
            ),
            location=(
                head_center.x
                - half_width
                * 0.91,
                front_y
                + 0.070,
                head_center.z
                - half_height
                * 0.02,
            ),
            width=(
                half_width
                * 0.20
            ),
            height=(
                half_height
                * 0.32
            ),
            depth=0.035,
            material=skin,
            parent_source=head,
        )
    )

    created.append(
        _create_flat_ellipse(
            name=(
                built_character.armature.name
                .removesuffix(
                    "_Rig"
                )
                + "_AnimeV3_Ear_R"
            ),
            location=(
                head_center.x
                + half_width
                * 0.91,
                front_y
                + 0.070,
                head_center.z
                - half_height
                * 0.02,
            ),
            width=(
                half_width
                * 0.20
            ),
            height=(
                half_height
                * 0.32
            ),
            depth=0.035,
            material=skin,
            parent_source=head,
        )
    )

    # Minimal anime nose cue instead of a 3D realistic nose.
    created.append(
        _create_prism_polygon(
            name=(
                built_character.armature.name
                .removesuffix(
                    "_Rig"
                )
                + "_AnimeV3_Nose"
            ),
            points=(
                (
                    -0.008,
                    0.045,
                ),
                (
                    0.030,
                    -0.020,
                ),
                (
                    -0.010,
                    -0.036,
                ),
            ),
            location=(
                head_center.x
                + 0.018,
                front_y
                - 0.020,
                head_center.z
                - half_height
                * 0.08,
            ),
            depth=0.008,
            material=nose_shadow,
            parent_source=head,
        )
    )

    # Strong upper-lash silhouettes make the eyes read as anime eyes.
    for label in (
        "Eye_L",
        "Eye_R",
    ):
        eye = face[
            label
        ]

        created.append(
            _create_tapered_line(
                name=(
                    eye.name
                    + "_UpperLash"
                ),
                location=(
                    eye.matrix_world.translation.x,
                    eye.matrix_world.translation.y
                    - 0.012,
                    eye.matrix_world.translation.z
                    + eye.dimensions.z
                    * 0.36,
                ),
                width=(
                    eye.dimensions.x
                    * 1.10
                ),
                height=max(
                    0.012,
                    eye.dimensions.z
                    * 0.12,
                ),
                material=ink,
                parent_source=eye,
                mirror=(
                    label
                    == "Eye_R"
                ),
            )
        )

    # Pointed front fringe: lightweight shallow prisms, not block slabs.
    prefix = (
        built_character.armature.name
        .removesuffix(
            "_Rig"
        )
    )

    strand_layout = (
        (
            -0.68,
            0.40,
            0.44,
        ),
        (
            -0.47,
            0.30,
            0.57,
        ),
        (
            -0.25,
            0.22,
            0.66,
        ),
        (
            0.00,
            0.20,
            0.72,
        ),
        (
            0.25,
            0.22,
            0.64,
        ),
        (
            0.47,
            0.30,
            0.55,
        ),
        (
            0.68,
            0.40,
            0.42,
        ),
    )

    for index, (
        x_factor,
        width_factor,
        length_factor,
    ) in enumerate(
        strand_layout,
        start=1,
    ):
        strand_width = (
            half_width
            * width_factor
        )

        strand_length = (
            half_height
            * length_factor
        )

        top_z = (
            head_center.z
            + half_height
            * 0.79
        )

        tip_z = (
            top_z
            - strand_length
        )

        x = (
            head_center.x
            + half_width
            * x_factor
        )

        lean = (
            x_factor
            * half_width
            * 0.12
        )

        created.append(
            _create_prism_polygon(
                name=(
                    prefix
                    + "_AnimeV3_Fringe_"
                    + f"{index:02d}"
                ),
                points=(
                    (
                        -strand_width
                        * 0.50,
                        strand_length
                        * 0.08,
                    ),
                    (
                        strand_width
                        * 0.50,
                        strand_length
                        * 0.08,
                    ),
                    (
                        strand_width
                        * 0.38
                        + lean,
                        -strand_length
                        * 0.55,
                    ),
                    (
                        lean,
                        -strand_length,
                    ),
                    (
                        -strand_width
                        * 0.34
                        + lean,
                        -strand_length
                        * 0.50,
                    ),
                ),
                location=(
                    x,
                    front_y
                    - 0.045,
                    top_z,
                ),
                depth=0.050,
                material=hair_material,
                parent_source=head,
            )
        )

    # Side locks frame the jaw instead of enclosing the entire face.
    for side, sign in (
        (
            "L",
            -1.0,
        ),
        (
            "R",
            1.0,
        ),
    ):
        created.append(
            _create_prism_polygon(
                name=(
                    prefix
                    + "_AnimeV3_SideLock_"
                    + side
                ),
                points=(
                    (
                        -half_width
                        * 0.11,
                        half_height
                        * 0.34,
                    ),
                    (
                        half_width
                        * 0.11,
                        half_height
                        * 0.34,
                    ),
                    (
                        half_width
                        * 0.08
                        * sign,
                        -half_height
                        * 0.38,
                    ),
                    (
                        -half_width
                        * 0.03
                        * sign,
                        -half_height
                        * 0.54,
                    ),
                ),
                location=(
                    head_center.x
                    + sign
                    * half_width
                    * 0.77,
                    front_y
                    - 0.015,
                    head_center.z
                    + half_height
                    * 0.05,
                ),
                depth=0.055,
                material=hair_material,
                parent_source=head,
            )
        )

    bpy.context.view_layer.update()

    return tuple(
        created
    )


def _head_object(
    built_character: BuiltCharacter,
) -> bpy.types.Object:
    for obj in (
        built_character.body_parts
    ):
        if obj.name.endswith(
            "_Body_Head"
        ):
            return obj

    raise AnimeCharacterV3Error(
        "Canonical head object not found."
    )


def _face_parts(
    built_character: BuiltCharacter,
) -> dict[
    str,
    bpy.types.Object,
]:
    prefix = (
        built_character.armature.name
        .removesuffix(
            "_Rig"
        )
    )

    marker = (
        prefix
        + "_Face_"
    )

    result = {}

    for obj in (
        built_character.face_parts
    ):
        if obj.name.startswith(
            marker
        ):
            result[
                obj.name[
                    len(marker):
                ]
            ] = obj

    required = {
        "Eye_L",
        "Eye_R",
        "Pupil_L",
        "Pupil_R",
        "Brow_L",
        "Brow_R",
        "Mouth",
    }

    missing = (
        required
        - set(result)
    )

    if missing:
        raise AnimeCharacterV3Error(
            "Missing canonical face parts: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    return result


def _smooth_mesh(
    obj: bpy.types.Object,
) -> None:
    if (
        obj.type
        != "MESH"
        or obj.data is None
    ):
        return

    for polygon in (
        obj.data.polygons
    ):
        polygon.use_smooth = True


def _first_material(
    obj: bpy.types.Object,
) -> bpy.types.Material | None:
    if (
        obj.type
        == "MESH"
        and obj.data is not None
        and len(
            obj.data.materials
        )
        > 0
    ):
        return (
            obj.data.materials[
                0
            ]
        )

    return None


def _material(
    name: str,
    rgba: tuple[
        float,
        float,
        float,
        float,
    ],
) -> bpy.types.Material:
    material = (
        bpy.data.materials.get(
            name
        )
    )

    if material is None:
        material = (
            bpy.data.materials.new(
                name=name
            )
        )

    material.diffuse_color = rgba

    return material


def _replace_with_almond(
    obj: bpy.types.Object,
    *,
    width_scale: float,
    height_scale: float,
) -> None:
    width = max(
        0.08,
        obj.dimensions.x
        * width_scale,
    )

    height = max(
        0.035,
        obj.dimensions.z
        * height_scale,
    )

    points = (
        (
            -width * 0.50,
            0.0,
        ),
        (
            -width * 0.26,
            height * 0.43,
        ),
        (
            0.08 * width,
            height * 0.50,
        ),
        (
            width * 0.50,
            0.0,
        ),
        (
            0.12 * width,
            -height * 0.43,
        ),
        (
            -width * 0.27,
            -height * 0.37,
        ),
    )

    _replace_mesh_with_prism(
        obj,
        points,
        depth=0.016,
    )


def _replace_with_ellipse(
    obj: bpy.types.Object,
    *,
    width_scale: float,
    height_scale: float,
    point_count: int,
) -> None:
    import math

    width = max(
        0.025,
        obj.dimensions.x
        * width_scale,
    )

    height = max(
        0.025,
        obj.dimensions.z
        * height_scale,
    )

    points = tuple(
        (
            math.cos(
                2.0
                * math.pi
                * index
                / point_count
            )
            * width
            * 0.50,
            math.sin(
                2.0
                * math.pi
                * index
                / point_count
            )
            * height
            * 0.50,
        )
        for index
        in range(
            point_count
        )
    )

    _replace_mesh_with_prism(
        obj,
        points,
        depth=0.012,
    )

    _smooth_mesh(
        obj
    )


def _replace_with_tapered_brow(
    obj: bpy.types.Object,
    *,
    mirror: bool,
) -> None:
    width = max(
        0.10,
        obj.dimensions.x
        * 1.30,
    )

    height = max(
        0.018,
        obj.dimensions.z
        * 0.78,
    )

    sign = (
        -1.0
        if mirror
        else 1.0
    )

    points = (
        (
            -width * 0.50,
            -height * 0.30,
        ),
        (
            width * 0.50,
            sign
            * height
            * 0.20,
        ),
        (
            width * 0.42,
            sign
            * height
            * 0.58,
        ),
        (
            -width * 0.48,
            height * 0.22,
        ),
    )

    _replace_mesh_with_prism(
        obj,
        points,
        depth=0.014,
    )


def _replace_with_mouth_shape(
    obj: bpy.types.Object,
) -> None:
    width = max(
        0.13,
        obj.dimensions.x
        * 0.88,
    )

    height = max(
        0.022,
        obj.dimensions.z
        * 1.65,
    )

    points = (
        (
            -width * 0.50,
            0.0,
        ),
        (
            -width * 0.22,
            height * 0.35,
        ),
        (
            width * 0.18,
            height * 0.30,
        ),
        (
            width * 0.50,
            0.02 * height,
        ),
        (
            width * 0.18,
            -height * 0.35,
        ),
        (
            -width * 0.22,
            -height * 0.30,
        ),
    )

    _replace_mesh_with_prism(
        obj,
        points,
        depth=0.012,
    )


def _replace_mesh_with_prism(
    obj: bpy.types.Object,
    points: tuple[
        tuple[
            float,
            float,
        ],
        ...,
    ],
    *,
    depth: float,
) -> None:
    materials = []

    if (
        obj.type
        == "MESH"
        and obj.data is not None
    ):
        materials = [
            material
            for material
            in obj.data.materials
            if material is not None
        ]

    old_mesh = (
        obj.data
        if obj.type
        == "MESH"
        else None
    )

    mesh = _prism_mesh(
        obj.name
        + "_AnimeV3Mesh",
        points,
        depth,
    )

    for material in materials:
        mesh.materials.append(
            material
        )

    obj.data = mesh

    obj.scale = (
        1.0,
        1.0,
        1.0,
    )

    if (
        old_mesh is not None
        and old_mesh.users == 0
    ):
        bpy.data.meshes.remove(
            old_mesh
        )


def _prism_mesh(
    name: str,
    points: tuple[
        tuple[
            float,
            float,
        ],
        ...,
    ],
    depth: float,
) -> bpy.types.Mesh:
    half_depth = (
        depth
        * 0.5
    )

    front = [
        (
            x,
            -half_depth,
            z,
        )
        for x, z
        in points
    ]

    back = [
        (
            x,
            half_depth,
            z,
        )
        for x, z
        in points
    ]

    vertices = (
        front
        + back
    )

    count = len(
        points
    )

    faces = [
        tuple(
            range(
                count
            )
        ),
        tuple(
            reversed(
                range(
                    count,
                    count * 2,
                )
            )
        ),
    ]

    for index in range(
        count
    ):
        nxt = (
            index + 1
        ) % count

        faces.append(
            (
                index,
                nxt,
                count + nxt,
                count + index,
            )
        )

    mesh = (
        bpy.data.meshes.new(
            name
        )
    )

    mesh.from_pydata(
        vertices,
        [],
        faces,
    )

    mesh.update()

    return mesh


def _create_prism_polygon(
    *,
    name: str,
    points: tuple[
        tuple[
            float,
            float,
        ],
        ...,
    ],
    location: tuple[
        float,
        float,
        float,
    ],
    depth: float,
    material: bpy.types.Material,
    parent_source: bpy.types.Object,
) -> bpy.types.Object:
    mesh = _prism_mesh(
        name
        + "_Mesh",
        points,
        depth,
    )

    mesh.materials.append(
        material
    )

    obj = (
        bpy.data.objects.new(
            name,
            mesh,
        )
    )

    bpy.context.collection.objects.link(
        obj
    )

    obj.location = Vector(
        location
    )

    _copy_parenting(
        parent_source,
        obj,
    )

    return obj


def _create_flat_ellipse(
    *,
    name: str,
    location: tuple[
        float,
        float,
        float,
    ],
    width: float,
    height: float,
    depth: float,
    material: bpy.types.Material,
    parent_source: bpy.types.Object,
) -> bpy.types.Object:
    import math

    points = tuple(
        (
            math.cos(
                2.0
                * math.pi
                * index
                / 12
            )
            * width
            * 0.50,
            math.sin(
                2.0
                * math.pi
                * index
                / 12
            )
            * height
            * 0.50,
        )
        for index
        in range(
            12
        )
    )

    obj = _create_prism_polygon(
        name=name,
        points=points,
        location=location,
        depth=depth,
        material=material,
        parent_source=parent_source,
    )

    _smooth_mesh(
        obj
    )

    return obj


def _create_tapered_line(
    *,
    name: str,
    location: tuple[
        float,
        float,
        float,
    ],
    width: float,
    height: float,
    material: bpy.types.Material,
    parent_source: bpy.types.Object,
    mirror: bool,
) -> bpy.types.Object:
    sign = (
        -1.0
        if mirror
        else 1.0
    )

    points = (
        (
            -width * 0.50,
            -height * 0.20,
        ),
        (
            width * 0.50,
            sign
            * height
            * 0.20,
        ),
        (
            width * 0.40,
            sign
            * height
            * 0.58,
        ),
        (
            -width * 0.46,
            height * 0.22,
        ),
    )

    return _create_prism_polygon(
        name=name,
        points=points,
        location=location,
        depth=0.010,
        material=material,
        parent_source=parent_source,
    )


def _copy_parenting(
    source: bpy.types.Object,
    target: bpy.types.Object,
) -> None:
    world = (
        target.matrix_world.copy()
    )

    target.parent = (
        source.parent
    )

    target.parent_type = (
        source.parent_type
    )

    target.parent_bone = (
        source.parent_bone
    )

    target.matrix_parent_inverse = (
        source.matrix_parent_inverse.copy()
    )

    target.matrix_world = world
