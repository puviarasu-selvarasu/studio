"""Lightweight retro-anime cinematic staging for Studio."""

from __future__ import annotations

import bpy

from mathutils import Vector


SUNSET = {
    "sky": (
        0.12,
        0.16,
        0.24,
        1.0,
    ),
    "horizon": (
        0.54,
        0.23,
        0.16,
        1.0,
    ),
    "sun": (
        1.00,
        0.72,
        0.34,
        1.0,
    ),
    "structure": (
        0.075,
        0.085,
        0.105,
        1.0,
    ),
    "platform": (
        0.21,
        0.20,
        0.18,
        1.0,
    ),
    "accent": (
        0.78,
        0.29,
        0.15,
        1.0,
    ),
}


NIGHT = {
    "sky": (
        0.018,
        0.035,
        0.080,
        1.0,
    ),
    "horizon": (
        0.045,
        0.075,
        0.120,
        1.0,
    ),
    "sun": (
        0.78,
        0.84,
        0.94,
        1.0,
    ),
    "structure": (
        0.018,
        0.025,
        0.040,
        1.0,
    ),
    "platform": (
        0.08,
        0.10,
        0.13,
        1.0,
    ),
    "accent": (
        0.20,
        0.34,
        0.50,
        1.0,
    ),
}


def create_retro_station_backdrop(
    *,
    variant: str,
) -> tuple[
    bpy.types.Object,
    ...,
]:
    """Create a cheap layered station composition for cel-style shots."""

    if variant == "sunset":
        palette = SUNSET
    elif variant == "night":
        palette = NIGHT
    else:
        raise ValueError(
            "variant must be sunset or night."
        )

    sky = _material(
        "StudioRetroSky_"
        + variant,
        palette[
            "sky"
        ],
    )

    horizon = _material(
        "StudioRetroHorizon_"
        + variant,
        palette[
            "horizon"
        ],
    )

    structure = _material(
        "StudioRetroStructure_"
        + variant,
        palette[
            "structure"
        ],
    )

    platform_material = _material(
        "StudioRetroPlatform_"
        + variant,
        palette[
            "platform"
        ],
    )

    accent = _material(
        "StudioRetroAccent_"
        + variant,
        palette[
            "accent"
        ],
    )

    light_disc = _material(
        "StudioRetroDisc_"
        + variant,
        palette[
            "sun"
        ],
    )

    objects: list[
        bpy.types.Object
    ] = []

    objects.append(
        _box(
            "StudioRetro_Sky",
            (
                0.0,
                4.8,
                1.5,
            ),
            (
                12.0,
                0.12,
                7.0,
            ),
            sky,
        )
    )

    objects.append(
        _box(
            "StudioRetro_Horizon",
            (
                0.0,
                4.55,
                -0.10,
            ),
            (
                12.0,
                0.10,
                2.2,
            ),
            horizon,
        )
    )

    objects.append(
        _disc(
            "StudioRetro_CelestialDisc",
            (
                2.5,
                4.30,
                2.25,
            ),
            0.66
            if variant
            == "sunset"
            else 0.92,
            light_disc,
        )
    )

    # Distant skyline cards.
    for index, (
        x,
        width,
        height,
    ) in enumerate(
        (
            (
                -4.0,
                0.8,
                1.0,
            ),
            (
                -2.9,
                1.1,
                1.5,
            ),
            (
                -1.7,
                0.6,
                0.9,
            ),
            (
                0.6,
                1.0,
                1.25,
            ),
            (
                1.7,
                0.6,
                1.8,
            ),
            (
                3.4,
                1.2,
                1.1,
            ),
        ),
        start=1,
    ):
        objects.append(
            _box(
                (
                    "StudioRetro_Distant_"
                    + f"{index:02d}"
                ),
                (
                    x,
                    4.10,
                    -0.15
                    + height
                    * 0.50,
                ),
                (
                    width,
                    0.09,
                    height,
                ),
                structure,
            )
        )

    # Station depth layers.
    objects.append(
        _box(
            "StudioRetro_Platform",
            (
                0.0,
                1.75,
                -1.55,
            ),
            (
                10.0,
                3.3,
                0.28,
            ),
            platform_material,
        )
    )

    objects.append(
        _box(
            "StudioRetro_PlatformEdge",
            (
                0.0,
                0.15,
                -1.38,
            ),
            (
                10.0,
                0.14,
                0.12,
            ),
            accent,
        )
    )

    for index, x in enumerate(
        (
            -2.55,
            2.55,
        ),
        start=1,
    ):
        objects.append(
            _box(
                (
                    "StudioRetro_Column_"
                    + str(
                        index
                    )
                ),
                (
                    x,
                    1.6,
                    0.25,
                ),
                (
                    0.18,
                    0.18,
                    3.9,
                ),
                structure,
            )
        )

    objects.append(
        _box(
            "StudioRetro_Canopy",
            (
                0.0,
                1.75,
                2.15,
            ),
            (
                6.4,
                1.55,
                0.20,
            ),
            structure,
        )
    )

    # Bench.
    objects.append(
        _box(
            "StudioRetro_BenchSeat",
            (
                1.75,
                1.0,
                -0.76,
            ),
            (
                1.65,
                0.46,
                0.16,
            ),
            accent,
        )
    )

    objects.append(
        _box(
            "StudioRetro_BenchBack",
            (
                1.75,
                1.22,
                -0.22,
            ),
            (
                1.65,
                0.14,
                0.78,
            ),
            accent,
        )
    )

    for x in (
        1.15,
        2.35,
    ):
        objects.append(
            _box(
                "StudioRetro_BenchLeg_"
                + str(
                    x
                ),
                (
                    x,
                    1.02,
                    -1.08,
                ),
                (
                    0.12,
                    0.14,
                    0.58,
                ),
                structure,
            )
        )

    # Foreground framing.
    objects.append(
        _box(
            "StudioRetro_ForegroundLeft",
            (
                -4.30,
                -0.20,
                0.20,
            ),
            (
                0.50,
                0.35,
                5.0,
            ),
            structure,
        )
    )

    objects.append(
        _box(
            "StudioRetro_ForegroundRight",
            (
                4.25,
                -0.05,
                0.55,
            ),
            (
                0.34,
                0.30,
                4.4,
            ),
            structure,
        )
    )

    return tuple(
        objects
    )


def apply_character_silhouette(
    objects: tuple[
        bpy.types.Object,
        ...,
    ],
) -> None:
    """Convert character render meshes into one dark graphic silhouette."""

    material = _material(
        "StudioRetroCharacterSilhouette",
        (
            0.008,
            0.012,
            0.022,
            1.0,
        ),
    )

    for obj in objects:
        if (
            obj.type
            != "MESH"
            or obj.data
            is None
        ):
            continue

        obj.data.materials.clear()

        obj.data.materials.append(
            material
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


def _box(
    name: str,
    location: tuple[
        float,
        float,
        float,
    ],
    dimensions: tuple[
        float,
        float,
        float,
    ],
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = (
        bpy.context.active_object
    )

    if obj is None:
        raise RuntimeError(
            "Unable to create cinematic box."
        )

    obj.name = name

    obj.dimensions = dimensions

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    obj.data.materials.append(
        material
    )

    return obj


def _disc(
    name: str,
    location: tuple[
        float,
        float,
        float,
    ],
    radius: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20,
        ring_count=10,
        location=location,
    )

    obj = (
        bpy.context.active_object
    )

    if obj is None:
        raise RuntimeError(
            "Unable to create celestial disc."
        )

    obj.name = name

    obj.scale = Vector(
        (
            radius,
            0.045,
            radius,
        )
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    obj.data.materials.append(
        material
    )

    for polygon in (
        obj.data.polygons
    ):
        polygon.use_smooth = True

    return obj
