"""Flat 2D/2.5D anime render proxy for Studio look development.

The canonical production rig remains authoritative for animation.
This module provides a lightweight graphic render representation so
the final frame does not expose low-poly facial geometry directly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import bpy


@dataclass(
    frozen=True,
    slots=True,
)
class AnimeLookProfile:
    skin: tuple[float, float, float, float]
    skin_shadow: tuple[float, float, float, float]

    hair: tuple[float, float, float, float]
    hair_light: tuple[float, float, float, float]

    ink: tuple[float, float, float, float]

    eye_white: tuple[float, float, float, float]
    iris: tuple[float, float, float, float]
    eye_highlight: tuple[float, float, float, float]

    outfit: tuple[float, float, float, float]
    outfit_shadow: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]

    sunset_top: tuple[float, float, float, float]
    sunset_low: tuple[float, float, float, float]

    night_top: tuple[float, float, float, float]
    night_low: tuple[float, float, float, float]


RETRO_MODERN_CEL_V1 = AnimeLookProfile(
    skin=(
        0.82,
        0.68,
        0.56,
        1.0,
    ),
    skin_shadow=(
        0.53,
        0.38,
        0.34,
        1.0,
    ),
    hair=(
        0.055,
        0.045,
        0.075,
        1.0,
    ),
    hair_light=(
        0.24,
        0.095,
        0.070,
        1.0,
    ),
    ink=(
        0.012,
        0.016,
        0.025,
        1.0,
    ),
    eye_white=(
        0.90,
        0.88,
        0.80,
        1.0,
    ),
    iris=(
        0.16,
        0.075,
        0.050,
        1.0,
    ),
    eye_highlight=(
        0.98,
        0.93,
        0.82,
        1.0,
    ),
    outfit=(
        0.10,
        0.12,
        0.18,
        1.0,
    ),
    outfit_shadow=(
        0.035,
        0.045,
        0.075,
        1.0,
    ),
    accent=(
        0.64,
        0.13,
        0.095,
        1.0,
    ),
    sunset_top=(
        0.055,
        0.085,
        0.145,
        1.0,
    ),
    sunset_low=(
        0.67,
        0.27,
        0.16,
        1.0,
    ),
    night_top=(
        0.012,
        0.025,
        0.065,
        1.0,
    ),
    night_low=(
        0.060,
        0.105,
        0.160,
        1.0,
    ),
)


_EXPRESSIONS = {
    "neutral": {
        "eye_open": 1.00,
        "pupil_x": 0.00,
        "pupil_z": 0.00,
        "brow_inner": 0.00,
        "mouth": 0.00,
    },
    "warm": {
        "eye_open": 0.88,
        "pupil_x": 0.02,
        "pupil_z": 0.01,
        "brow_inner": 0.05,
        "mouth": 0.07,
    },
    "sad": {
        "eye_open": 0.78,
        "pupil_x": -0.01,
        "pupil_z": -0.035,
        "brow_inner": 0.12,
        "mouth": -0.08,
    },
    "determined": {
        "eye_open": 0.70,
        "pupil_x": 0.035,
        "pupil_z": 0.01,
        "brow_inner": -0.12,
        "mouth": -0.015,
    },
}


def build_retro_modern_anime_portrait(
    *,
    expression: str = "determined",
    mood: str = "sunset",
    profile: AnimeLookProfile = RETRO_MODERN_CEL_V1,
) -> tuple[
    bpy.types.Object,
    ...,
]:
    """Create a flat graphic anime keyframe using only lightweight meshes."""

    if expression not in _EXPRESSIONS:
        raise ValueError(
            "Unsupported expression: "
            + expression
        )

    if mood not in {
        "sunset",
        "night",
    }:
        raise ValueError(
            "mood must be sunset or night."
        )

    acting = (
        _EXPRESSIONS[
            expression
        ]
    )

    materials = {
        "skin": _material(
            "AnimeProxy_Skin",
            profile.skin,
        ),
        "skin_shadow": _material(
            "AnimeProxy_SkinShadow",
            profile.skin_shadow,
        ),
        "hair": _material(
            "AnimeProxy_Hair",
            profile.hair,
        ),
        "hair_light": _material(
            "AnimeProxy_HairLight",
            profile.hair_light,
        ),
        "ink": _material(
            "AnimeProxy_Ink",
            profile.ink,
        ),
        "eye_white": _material(
            "AnimeProxy_EyeWhite",
            profile.eye_white,
        ),
        "iris": _material(
            "AnimeProxy_Iris",
            profile.iris,
        ),
        "highlight": _material(
            "AnimeProxy_EyeHighlight",
            profile.eye_highlight,
        ),
        "outfit": _material(
            "AnimeProxy_Outfit",
            profile.outfit,
        ),
        "outfit_shadow": _material(
            "AnimeProxy_OutfitShadow",
            profile.outfit_shadow,
        ),
        "accent": _material(
            "AnimeProxy_Accent",
            profile.accent,
        ),
        "sky_top": _material(
            "AnimeProxy_SkyTop_"
            + mood,
            (
                profile.sunset_top
                if mood
                == "sunset"
                else profile.night_top
            ),
        ),
        "sky_low": _material(
            "AnimeProxy_SkyLow_"
            + mood,
            (
                profile.sunset_low
                if mood
                == "sunset"
                else profile.night_low
            ),
        ),
        "sun": _material(
            "AnimeProxy_Celestial_"
            + mood,
            (
                (
                    0.98,
                    0.72,
                    0.36,
                    1.0,
                )
                if mood
                == "sunset"
                else (
                    0.78,
                    0.84,
                    0.94,
                    1.0,
                )
            ),
        ),
        "distance": _material(
            "AnimeProxy_Distance_"
            + mood,
            (
                (
                    0.12,
                    0.10,
                    0.13,
                    1.0,
                )
                if mood
                == "sunset"
                else (
                    0.018,
                    0.035,
                    0.065,
                    1.0,
                )
            ),
        ),
        "lamp": _material(
            "AnimeProxy_Lamp",
            (
                0.95,
                0.55,
                0.22,
                1.0,
            ),
        ),
    }

    objects: list[
        bpy.types.Object
    ] = []

    # -----------------------------------------------------
    # BACKGROUND ? flat painted-style layers.
    # -----------------------------------------------------

    objects.append(
        _rect(
            "AnimeProxy_SkyTop",
            (
                -5.2,
                2.9,
            ),
            (
                10.4,
                3.0,
            ),
            y=2.20,
            material=materials[
                "sky_top"
            ],
        )
    )

    objects.append(
        _rect(
            "AnimeProxy_SkyLow",
            (
                -5.2,
                -0.2,
            ),
            (
                10.4,
                3.4,
            ),
            y=2.18,
            material=materials[
                "sky_low"
            ],
        )
    )

    celestial_x = (
        2.55
        if mood
        == "sunset"
        else 2.75
    )

    celestial_z = (
        1.15
        if mood
        == "sunset"
        else 1.40
    )

    objects.append(
        _ellipse(
            "AnimeProxy_CelestialDisc",
            celestial_x,
            celestial_z,
            (
                0.44
                if mood
                == "sunset"
                else 0.61
            ),
            (
                0.44
                if mood
                == "sunset"
                else 0.61
            ),
            y=2.05,
            material=materials[
                "sun"
            ],
            point_count=32,
        )
    )

    # Distant mountain / roof silhouette.
    objects.append(
        _polygon(
            "AnimeProxy_DistantSilhouette",
            (
                (
                    -5.2,
                    -0.10,
                ),
                (
                    -4.0,
                    0.55,
                ),
                (
                    -3.15,
                    0.18,
                ),
                (
                    -2.15,
                    0.82,
                ),
                (
                    -1.15,
                    0.14,
                ),
                (
                    -0.15,
                    0.58,
                ),
                (
                    0.95,
                    0.10,
                ),
                (
                    1.75,
                    0.52,
                ),
                (
                    2.75,
                    0.04,
                ),
                (
                    3.75,
                    0.42,
                ),
                (
                    5.2,
                    -0.08,
                ),
                (
                    5.2,
                    -1.35,
                ),
                (
                    -5.2,
                    -1.35,
                ),
            ),
            y=1.85,
            material=materials[
                "distance"
            ],
        )
    )

    # Station architecture ? graphic shapes rather than 3D blocks.
    objects.append(
        _rect(
            "AnimeProxy_StationRoof",
            (
                -5.2,
                2.10,
            ),
            (
                10.4,
                0.18,
            ),
            y=1.62,
            material=materials[
                "ink"
            ],
        )
    )

    for index, x in enumerate(
        (
            -3.65,
            2.95,
        ),
        start=1,
    ):
        objects.append(
            _rect(
                (
                    "AnimeProxy_StationPost_"
                    + str(index)
                ),
                (
                    x,
                    -1.20,
                ),
                (
                    0.11,
                    3.35,
                ),
                y=1.60,
                material=materials[
                    "ink"
                ],
            )
        )

    objects.append(
        _rect(
            "AnimeProxy_PlatformLine",
            (
                -5.2,
                -1.28,
            ),
            (
                10.4,
                0.13,
            ),
            y=1.58,
            material=materials[
                "accent"
            ],
        )
    )

    # Small warm station lamps.
    for index, x in enumerate(
        (
            -3.0,
            1.85,
        ),
        start=1,
    ):
        objects.append(
            _ellipse(
                (
                    "AnimeProxy_Lamp_"
                    + str(index)
                ),
                x,
                1.52,
                0.075,
                0.13,
                y=1.52,
                material=materials[
                    "lamp"
                ],
                point_count=12,
            )
        )

    # -----------------------------------------------------
    # CHARACTER ? deliberately flat render representation.
    # -----------------------------------------------------

    cx = -0.62

    # Back hair silhouette.
    hair_back = (
        (
            cx - 1.24,
            1.56,
        ),
        (
            cx - 0.92,
            2.02,
        ),
        (
            cx - 0.32,
            2.26,
        ),
        (
            cx + 0.38,
            2.20,
        ),
        (
            cx + 0.95,
            1.92,
        ),
        (
            cx + 1.23,
            1.43,
        ),
        (
            cx + 1.30,
            0.52,
        ),
        (
            cx + 1.22,
            -0.46,
        ),
        (
            cx + 0.88,
            -1.12,
        ),
        (
            cx + 0.50,
            -1.55,
        ),
        (
            cx - 0.62,
            -1.58,
        ),
        (
            cx - 1.04,
            -1.08,
        ),
        (
            cx - 1.30,
            -0.32,
        ),
        (
            cx - 1.34,
            0.72,
        ),
    )

    objects.extend(
        _layered_shape(
            "AnimeProxy_HairBack",
            hair_back,
            y=0.32,
            material=materials[
                "hair"
            ],
            ink=materials[
                "ink"
            ],
            outline_scale=1.025,
        )
    )

    # Shoulders / coat.
    shoulders = (
        (
            cx - 1.95,
            -2.70,
        ),
        (
            cx - 1.62,
            -1.68,
        ),
        (
            cx - 0.75,
            -1.30,
        ),
        (
            cx,
            -1.18,
        ),
        (
            cx + 0.75,
            -1.30,
        ),
        (
            cx + 1.58,
            -1.70,
        ),
        (
            cx + 2.05,
            -2.70,
        ),
    )

    objects.extend(
        _layered_shape(
            "AnimeProxy_Shoulders",
            shoulders,
            y=0.24,
            material=materials[
                "outfit"
            ],
            ink=materials[
                "ink"
            ],
            outline_scale=1.025,
        )
    )

    # Coat shadow creates a strong cel-value split.
    objects.append(
        _polygon(
            "AnimeProxy_OutfitShadow",
            (
                (
                    cx + 0.18,
                    -1.25,
                ),
                (
                    cx + 0.82,
                    -1.35,
                ),
                (
                    cx + 1.62,
                    -1.74,
                ),
                (
                    cx + 2.05,
                    -2.70,
                ),
                (
                    cx + 0.35,
                    -2.70,
                ),
            ),
            y=0.18,
            material=materials[
                "outfit_shadow"
            ],
        )
    )

    # Neck.
    neck = (
        (
            cx - 0.30,
            -1.34,
        ),
        (
            cx + 0.30,
            -1.34,
        ),
        (
            cx + 0.27,
            -1.88,
        ),
        (
            cx - 0.27,
            -1.88,
        ),
    )

    objects.extend(
        _layered_shape(
            "AnimeProxy_Neck",
            neck,
            y=0.14,
            material=materials[
                "skin"
            ],
            ink=materials[
                "ink"
            ],
            outline_scale=1.04,
        )
    )

    # Collar accent.
    objects.append(
        _polygon(
            "AnimeProxy_CollarAccent",
            (
                (
                    cx - 0.32,
                    -1.69,
                ),
                (
                    cx,
                    -1.93,
                ),
                (
                    cx + 0.32,
                    -1.69,
                ),
                (
                    cx + 0.22,
                    -1.57,
                ),
                (
                    cx,
                    -1.73,
                ),
                (
                    cx - 0.22,
                    -1.57,
                ),
            ),
            y=0.06,
            material=materials[
                "accent"
            ],
        )
    )

    # Ears.
    for side, x in (
        (
            "L",
            cx - 1.03,
        ),
        (
            "R",
            cx + 1.03,
        ),
    ):
        objects.extend(
            _layered_shape(
                (
                    "AnimeProxy_Ear_"
                    + side
                ),
                _ellipse_points(
                    x,
                    0.28,
                    0.22,
                    0.43,
                    16,
                ),
                y=0.06,
                material=materials[
                    "skin"
                ],
                ink=materials[
                    "ink"
                ],
                outline_scale=1.05,
            )
        )

    # Human/anime face silhouette with tapered chin.
    face = (
        (
            cx - 0.96,
            1.35,
        ),
        (
            cx - 1.08,
            0.88,
        ),
        (
            cx - 1.05,
            0.28,
        ),
        (
            cx - 0.93,
            -0.34,
        ),
        (
            cx - 0.68,
            -0.84,
        ),
        (
            cx - 0.32,
            -1.20,
        ),
        (
            cx,
            -1.37,
        ),
        (
            cx + 0.32,
            -1.20,
        ),
        (
            cx + 0.70,
            -0.82,
        ),
        (
            cx + 0.97,
            -0.30,
        ),
        (
            cx + 1.08,
            0.34,
        ),
        (
            cx + 1.04,
            0.90,
        ),
        (
            cx + 0.88,
            1.34,
        ),
        (
            cx + 0.42,
            1.58,
        ),
        (
            cx - 0.46,
            1.58,
        ),
    )

    objects.extend(
        _layered_shape(
            "AnimeProxy_Face",
            face,
            y=0.00,
            material=materials[
                "skin"
            ],
            ink=materials[
                "ink"
            ],
            outline_scale=1.035,
        )
    )

    # Single hard-edged cel shadow, deliberately graphic.
    objects.append(
        _polygon(
            "AnimeProxy_FaceCelShadow",
            (
                (
                    cx + 0.18,
                    1.53,
                ),
                (
                    cx + 0.88,
                    1.32,
                ),
                (
                    cx + 1.06,
                    0.74,
                ),
                (
                    cx + 1.00,
                    -0.27,
                ),
                (
                    cx + 0.69,
                    -0.82,
                ),
                (
                    cx + 0.32,
                    -1.20,
                ),
                (
                    cx + 0.08,
                    -1.31,
                ),
                (
                    cx + 0.26,
                    -0.58,
                ),
                (
                    cx + 0.25,
                    0.18,
                ),
            ),
            y=-0.022,
            material=materials[
                "skin_shadow"
            ],
        )
    )

    # Eyes.
    eye_z = 0.45

    eye_open = float(
        acting[
            "eye_open"
        ]
    )

    pupil_shift_x = float(
        acting[
            "pupil_x"
        ]
    )

    pupil_shift_z = float(
        acting[
            "pupil_z"
        ]
    )

    for side, eye_x, tilt in (
        (
            "L",
            cx - 0.43,
            0.025,
        ),
        (
            "R",
            cx + 0.45,
            -0.015,
        ),
    ):
        eye_points = _almond_points(
            eye_x,
            eye_z,
            0.66,
            0.25
            * eye_open,
            tilt,
        )

        objects.extend(
            _layered_shape(
                (
                    "AnimeProxy_Eye_"
                    + side
                ),
                eye_points,
                y=-0.070,
                material=materials[
                    "eye_white"
                ],
                ink=materials[
                    "ink"
                ],
                outline_scale=1.075,
            )
        )

        iris_x = (
            eye_x
            + pupil_shift_x
            + (
                0.018
                if side
                == "R"
                else 0.0
            )
        )

        iris_z = (
            eye_z
            + pupil_shift_z
        )

        objects.append(
            _ellipse(
                (
                    "AnimeProxy_Iris_"
                    + side
                ),
                iris_x,
                iris_z,
                0.145,
                0.205
                * max(
                    0.76,
                    eye_open,
                ),
                y=-0.105,
                material=materials[
                    "iris"
                ],
                point_count=18,
            )
        )

        objects.append(
            _ellipse(
                (
                    "AnimeProxy_EyeHighlight_"
                    + side
                ),
                iris_x - 0.036,
                iris_z + 0.066,
                0.036,
                0.050,
                y=-0.125,
                material=materials[
                    "highlight"
                ],
                point_count=12,
            )
        )

        # Thick upper lash = important retro anime read.
        lash_z = (
            eye_z
            + 0.12
            * eye_open
        )

        objects.append(
            _polygon(
                (
                    "AnimeProxy_UpperLash_"
                    + side
                ),
                (
                    (
                        eye_x - 0.36,
                        lash_z - 0.010,
                    ),
                    (
                        eye_x + 0.34,
                        lash_z + tilt,
                    ),
                    (
                        eye_x + 0.30,
                        lash_z + 0.055,
                    ),
                    (
                        eye_x - 0.34,
                        lash_z + 0.050,
                    ),
                ),
                y=-0.145,
                material=materials[
                    "ink"
                ],
            )
        )

    # Brows.
    brow_inner = float(
        acting[
            "brow_inner"
        ]
    )

    left_brow = (
        (
            cx - 0.77,
            0.88,
        ),
        (
            cx - 0.14,
            0.85
            + brow_inner,
        ),
        (
            cx - 0.18,
            0.91
            + brow_inner,
        ),
        (
            cx - 0.75,
            0.94,
        ),
    )

    right_brow = (
        (
            cx + 0.16,
            0.85
            + brow_inner,
        ),
        (
            cx + 0.79,
            0.88,
        ),
        (
            cx + 0.77,
            0.94,
        ),
        (
            cx + 0.20,
            0.91
            + brow_inner,
        ),
    )

    objects.append(
        _polygon(
            "AnimeProxy_Brow_L",
            left_brow,
            y=-0.150,
            material=materials[
                "ink"
            ],
        )
    )

    objects.append(
        _polygon(
            "AnimeProxy_Brow_R",
            right_brow,
            y=-0.150,
            material=materials[
                "ink"
            ],
        )
    )

    # Minimal nose cue, keeping classic anime economy.
    objects.append(
        _polygon(
            "AnimeProxy_NoseCue",
            (
                (
                    cx + 0.055,
                    0.18,
                ),
                (
                    cx + 0.12,
                    -0.03,
                ),
                (
                    cx + 0.045,
                    -0.08,
                ),
            ),
            y=-0.155,
            material=materials[
                "skin_shadow"
            ],
        )
    )

    # Emotion-aware restrained mouth.
    mouth_curve = float(
        acting[
            "mouth"
        ]
    )

    mouth_z = -0.48

    mouth_points = (
        (
            cx - 0.20,
            mouth_z
            + mouth_curve
            * 0.25,
        ),
        (
            cx - 0.055,
            mouth_z
            + mouth_curve,
        ),
        (
            cx + 0.16,
            mouth_z
            + mouth_curve
            * 0.18,
        ),
        (
            cx + 0.12,
            mouth_z
            - 0.035,
        ),
        (
            cx - 0.07,
            mouth_z
            - 0.045,
        ),
        (
            cx - 0.20,
            mouth_z
            - 0.015,
        ),
    )

    objects.append(
        _polygon(
            "AnimeProxy_Mouth",
            mouth_points,
            y=-0.160,
            material=materials[
                "ink"
            ],
        )
    )

    # Hair fringe ? varied graphic clumps rather than cuboids.
    fringe_shapes = (
        (
            (
                cx - 1.00,
                1.45,
            ),
            (
                cx - 0.60,
                1.92,
            ),
            (
                cx - 0.32,
                1.72,
            ),
            (
                cx - 0.50,
                0.92,
            ),
            (
                cx - 0.78,
                1.14,
            ),
        ),
        (
            (
                cx - 0.62,
                1.78,
            ),
            (
                cx - 0.18,
                2.02,
            ),
            (
                cx + 0.02,
                1.82,
            ),
            (
                cx - 0.10,
                0.78,
            ),
            (
                cx - 0.38,
                1.10,
            ),
        ),
        (
            (
                cx - 0.10,
                1.86,
            ),
            (
                cx + 0.34,
                2.00,
            ),
            (
                cx + 0.52,
                1.70,
            ),
            (
                cx + 0.31,
                0.94,
            ),
            (
                cx + 0.10,
                0.70,
            ),
        ),
        (
            (
                cx + 0.34,
                1.82,
            ),
            (
                cx + 0.78,
                1.84,
            ),
            (
                cx + 1.00,
                1.42,
            ),
            (
                cx + 0.70,
                0.91,
            ),
            (
                cx + 0.48,
                1.16,
            ),
        ),
    )

    for index, points in enumerate(
        fringe_shapes,
        start=1,
    ):
        objects.extend(
            _layered_shape(
                (
                    "AnimeProxy_Fringe_"
                    + str(index)
                ),
                points,
                y=-0.205,
                material=materials[
                    "hair"
                ],
                ink=materials[
                    "ink"
                ],
                outline_scale=1.035,
            )
        )

    # Hand-painted-feeling hair highlight strip.
    objects.append(
        _polygon(
            "AnimeProxy_HairHighlight",
            (
                (
                    cx - 0.90,
                    1.66,
                ),
                (
                    cx - 0.38,
                    1.95,
                ),
                (
                    cx + 0.22,
                    1.94,
                ),
                (
                    cx + 0.62,
                    1.72,
                ),
                (
                    cx + 0.48,
                    1.64,
                ),
                (
                    cx - 0.35,
                    1.76,
                ),
            ),
            y=-0.230,
            material=materials[
                "hair_light"
            ],
        )
    )

    bpy.context.view_layer.update()

    return tuple(
        objects
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


def _polygon(
    name: str,
    points: tuple[
        tuple[
            float,
            float,
        ],
        ...,
    ],
    *,
    y: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    vertices = [
        (
            x,
            y,
            z,
        )
        for x, z
        in points
    ]

    mesh = bpy.data.meshes.new(
        name
        + "_Mesh"
    )

    mesh.from_pydata(
        vertices,
        [],
        [
            tuple(
                range(
                    len(
                        vertices
                    )
                )
            )
        ],
    )

    mesh.update()

    obj = bpy.data.objects.new(
        name,
        mesh,
    )

    bpy.context.collection.objects.link(
        obj
    )

    mesh.materials.append(
        material
    )

    return obj


def _layered_shape(
    name: str,
    points: tuple[
        tuple[
            float,
            float,
        ],
        ...,
    ],
    *,
    y: float,
    material: bpy.types.Material,
    ink: bpy.types.Material,
    outline_scale: float,
) -> tuple[
    bpy.types.Object,
    bpy.types.Object,
]:
    outline_points = (
        _scale_points(
            points,
            outline_scale,
        )
    )

    outline = _polygon(
        name
        + "_Ink",
        outline_points,
        y=y + 0.018,
        material=ink,
    )

    fill = _polygon(
        name,
        points,
        y=y,
        material=material,
    )

    return (
        outline,
        fill,
    )


def _scale_points(
    points: tuple[
        tuple[
            float,
            float,
        ],
        ...,
    ],
    scale: float,
) -> tuple[
    tuple[
        float,
        float,
    ],
    ...,
]:
    cx = sum(
        point[
            0
        ]
        for point
        in points
    ) / len(
        points
    )

    cz = sum(
        point[
            1
        ]
        for point
        in points
    ) / len(
        points
    )

    return tuple(
        (
            cx
            + (
                x - cx
            )
            * scale,
            cz
            + (
                z - cz
            )
            * scale,
        )
        for x, z
        in points
    )


def _rect(
    name: str,
    lower_left: tuple[
        float,
        float,
    ],
    size: tuple[
        float,
        float,
    ],
    *,
    y: float,
    material: bpy.types.Material,
) -> bpy.types.Object:
    x, z = lower_left
    width, height = size

    return _polygon(
        name,
        (
            (
                x,
                z,
            ),
            (
                x + width,
                z,
            ),
            (
                x + width,
                z + height,
            ),
            (
                x,
                z + height,
            ),
        ),
        y=y,
        material=material,
    )


def _ellipse(
    name: str,
    cx: float,
    cz: float,
    rx: float,
    rz: float,
    *,
    y: float,
    material: bpy.types.Material,
    point_count: int,
) -> bpy.types.Object:
    return _polygon(
        name,
        _ellipse_points(
            cx,
            cz,
            rx,
            rz,
            point_count,
        ),
        y=y,
        material=material,
    )


def _ellipse_points(
    cx: float,
    cz: float,
    rx: float,
    rz: float,
    point_count: int,
) -> tuple[
    tuple[
        float,
        float,
    ],
    ...,
]:
    return tuple(
        (
            cx
            + math.cos(
                2.0
                * math.pi
                * index
                / point_count
            )
            * rx,
            cz
            + math.sin(
                2.0
                * math.pi
                * index
                / point_count
            )
            * rz,
        )
        for index
        in range(
            point_count
        )
    )


def _almond_points(
    cx: float,
    cz: float,
    width: float,
    height: float,
    tilt: float,
) -> tuple[
    tuple[
        float,
        float,
    ],
    ...,
]:
    return (
        (
            cx - width
            * 0.50,
            cz,
        ),
        (
            cx - width
            * 0.23,
            cz
            + height
            * 0.47,
        ),
        (
            cx + width
            * 0.12,
            cz
            + height
            * 0.52
            + tilt,
        ),
        (
            cx + width
            * 0.50,
            cz
            + tilt,
        ),
        (
            cx + width
            * 0.12,
            cz
            - height
            * 0.42
            + tilt,
        ),
        (
            cx - width
            * 0.25,
            cz
            - height
            * 0.38,
        ),
    )
