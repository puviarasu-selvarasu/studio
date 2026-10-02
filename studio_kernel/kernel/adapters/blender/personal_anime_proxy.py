"""Generic lightweight identity proof renderer.

This adapter exists only to verify that arbitrary capture profiles drive
different visual identity cues. Phase 15 replaces this proof representation
with Studio's true 2D anime drawing system.
"""

from __future__ import annotations

import math

import bpy

from kernel.characters.personal_capture import (
    PersonalAnimeCaptureProfile,
)


def build_personal_identity_proof(
    profile: PersonalAnimeCaptureProfile,
    *,
    view: str,
) -> tuple[
    bpy.types.Object,
    ...,
]:
    if view not in {
        "front",
        "profile",
        "full_body",
    }:
        raise ValueError(
            "Unsupported identity-proof view."
        )

    palette = _palette(
        profile
    )

    objects: list[
        bpy.types.Object
    ] = []

    objects.extend(
        _background(
            palette
        )
    )

    if view == "front":
        objects.extend(
            _front(
                profile,
                palette,
            )
        )

    elif view == "profile":
        objects.extend(
            _profile(
                profile,
                palette,
            )
        )

    else:
        objects.extend(
            _full_body(
                profile,
                palette,
            )
        )

    bpy.context.view_layer.update()

    return tuple(
        objects
    )


def _hex(
    value: str,
) -> tuple[
    float,
    float,
    float,
    float,
]:
    return (
        int(
            value[
                1:3
            ],
            16,
        )
        / 255.0,
        int(
            value[
                3:5
            ],
            16,
        )
        / 255.0,
        int(
            value[
                5:7
            ],
            16,
        )
        / 255.0,
        1.0,
    )


def _darken(
    rgba: tuple[
        float,
        float,
        float,
        float,
    ],
    factor: float,
) -> tuple[
    float,
    float,
    float,
    float,
]:
    return (
        rgba[0]
        * factor,
        rgba[1]
        * factor,
        rgba[2]
        * factor,
        1.0,
    )


def _palette(
    profile: PersonalAnimeCaptureProfile,
) -> dict[
    str,
    bpy.types.Material,
]:
    prefix = (
        "IdentityProof_"
        + profile.character_id
        + "_"
    )

    skin = _hex(
        profile.skin_color
    )

    hair = _hex(
        profile.hair_color
    )

    eye = _hex(
        profile.eye_color
    )

    outfit = _hex(
        profile.outfit_color
    )

    return {
        "ink": _material(
            prefix + "Ink",
            (
                0.008,
                0.010,
                0.016,
                1.0,
            ),
        ),
        "skin": _material(
            prefix + "Skin",
            skin,
        ),
        "skin_shadow": _material(
            prefix + "SkinShadow",
            _darken(
                skin,
                0.66,
            ),
        ),
        "hair": _material(
            prefix + "Hair",
            hair,
        ),
        "hair_light": _material(
            prefix + "HairLight",
            tuple(
                min(
                    1.0,
                    channel
                    * 2.0
                    + 0.025,
                )
                for channel
                in hair[
                    :3
                ]
            )
            + (
                1.0,
            ),
        ),
        "beard": _material(
            prefix + "FacialHair",
            _darken(
                hair,
                0.86,
            ),
        ),
        "eye_white": _material(
            prefix + "EyeWhite",
            (
                0.89,
                0.87,
                0.82,
                1.0,
            ),
        ),
        "eye": _material(
            prefix + "Eye",
            eye,
        ),
        "outfit": _material(
            prefix + "Outfit",
            outfit,
        ),
        "sky": _material(
            prefix + "Sky",
            (
                0.025,
                0.060,
                0.105,
                1.0,
            ),
        ),
        "horizon": _material(
            prefix + "Horizon",
            (
                0.52,
                0.25,
                0.16,
                1.0,
            ),
        ),
        "distance": _material(
            prefix + "Distance",
            (
                0.10,
                0.09,
                0.13,
                1.0,
            ),
        ),
    }


def _background(
    palette: dict[
        str,
        bpy.types.Material,
    ],
) -> list[
    bpy.types.Object
]:
    return [
        _rect(
            "IdentityProof_Sky",
            (
                -5.5,
                -2.8,
            ),
            (
                11.0,
                6.2,
            ),
            y=2.4,
            material=palette[
                "sky"
            ],
        ),

        _rect(
            "IdentityProof_Horizon",
            (
                -5.5,
                -1.0,
            ),
            (
                11.0,
                2.0,
            ),
            y=2.35,
            material=palette[
                "horizon"
            ],
        ),

        _polygon(
            "IdentityProof_Distance",
            (
                (
                    -5.5,
                    -0.8,
                ),
                (
                    -4.2,
                    0.0,
                ),
                (
                    -3.0,
                    -0.55,
                ),
                (
                    -1.8,
                    0.20,
                ),
                (
                    -0.5,
                    -0.48,
                ),
                (
                    0.9,
                    0.10,
                ),
                (
                    2.2,
                    -0.50,
                ),
                (
                    3.7,
                    0.0,
                ),
                (
                    5.5,
                    -0.60,
                ),
                (
                    5.5,
                    -2.5,
                ),
                (
                    -5.5,
                    -2.5,
                ),
            ),
            y=2.1,
            material=palette[
                "distance"
            ],
        ),
    ]


def _face_dimensions(
    profile: PersonalAnimeCaptureProfile,
) -> tuple[
    float,
    float,
]:
    widths = {
        "oval": 0.98,
        "tapered_oval": 0.94,
        "round": 1.06,
        "square": 1.05,
        "heart": 0.98,
        "long": 0.91,
    }

    heights = {
        "oval": 1.45,
        "tapered_oval": 1.50,
        "round": 1.34,
        "square": 1.40,
        "heart": 1.43,
        "long": 1.58,
    }

    return (
        widths[
            profile.face_shape
        ]
        * profile.head_scale,
        heights[
            profile.face_shape
        ]
        * profile.head_scale,
    )


def _front(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
) -> list[
    bpy.types.Object
]:
    result: list[
        bpy.types.Object
    ] = []

    face_width, face_height = (
        _face_dimensions(
            profile
        )
    )

    shoulder = (
        1.60
        * profile.shoulder_scale
    )

    result.extend(
        _layered(
            "IdentityProof_Front_Shoulders",
            (
                (
                    -shoulder,
                    -2.7,
                ),
                (
                    -shoulder
                    * 0.82,
                    -1.62,
                ),
                (
                    -0.60,
                    -1.28,
                ),
                (
                    0.60,
                    -1.28,
                ),
                (
                    shoulder
                    * 0.82,
                    -1.62,
                ),
                (
                    shoulder,
                    -2.7,
                ),
            ),
            y=0.30,
            fill=palette[
                "outfit"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.025,
        )
    )

    face = _front_face_points(
        face_width,
        face_height,
        profile.face_shape,
    )

    result.extend(
        _layered(
            "IdentityProof_Front_Face",
            face,
            y=0.0,
            fill=palette[
                "skin"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.035,
        )
    )

    result.append(
        _polygon(
            "IdentityProof_Front_Shadow",
            (
                (
                    0.15,
                    1.25,
                ),
                (
                    face_width
                    * 0.90,
                    1.05,
                ),
                (
                    face_width
                    * 0.84,
                    -0.30,
                ),
                (
                    0.30,
                    -1.20,
                ),
                (
                    0.05,
                    -1.34,
                ),
                (
                    0.16,
                    -0.30,
                ),
            ),
            y=-0.03,
            material=palette[
                "skin_shadow"
            ],
        )
    )

    eye_height = (
        0.19
        if profile.eye_shape
        == "almond"
        else 0.23
        if profile.eye_shape
        == "round"
        else 0.14
    )

    for side, x in (
        (
            "L",
            -0.41,
        ),
        (
            "R",
            0.41,
        ),
    ):
        result.extend(
            _layered(
                (
                    "IdentityProof_Front_Eye_"
                    + side
                ),
                _almond(
                    x,
                    0.42,
                    0.62,
                    eye_height,
                ),
                y=-0.08,
                fill=palette[
                    "eye_white"
                ],
                ink=palette[
                    "ink"
                ],
                outline=1.06,
            )
        )

        result.append(
            _ellipse(
                (
                    "IdentityProof_Front_Iris_"
                    + side
                ),
                x,
                0.42,
                0.105,
                0.15,
                y=-0.12,
                material=palette[
                    "eye"
                ],
                count=16,
            )
        )

    brow_height = {
        "thin": 0.045,
        "medium": 0.075,
        "thick": 0.11,
    }[
        profile.brow_style
    ]

    for side, x in (
        (
            "L",
            -0.45,
        ),
        (
            "R",
            0.45,
        ),
    ):
        result.append(
            _rect(
                (
                    "IdentityProof_Brow_"
                    + side
                ),
                (
                    x - 0.30,
                    0.79,
                ),
                (
                    0.60,
                    brow_height,
                ),
                y=-0.14,
                material=palette[
                    "hair"
                ],
            )
        )

    nose_depth = {
        "soft": 0.05,
        "straight": 0.08,
        "prominent": 0.13,
        "convex": 0.15,
    }[
        profile.nose_profile
    ]

    result.append(
        _polygon(
            "IdentityProof_Front_Nose",
            (
                (
                    0.02,
                    0.23,
                ),
                (
                    nose_depth,
                    -0.13,
                ),
                (
                    -0.02,
                    -0.18,
                ),
            ),
            y=-0.15,
            material=palette[
                "skin_shadow"
            ],
        )
    )

    result.extend(
        _front_hair(
            profile,
            palette,
            face_width,
        )
    )

    result.extend(
        _front_facial_hair(
            profile,
            palette,
            face_width,
        )
    )

    return result


def _profile(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
) -> list[
    bpy.types.Object
]:
    result: list[
        bpy.types.Object
    ] = []

    face_width, face_height = (
        _face_dimensions(
            profile
        )
    )

    nose = {
        "soft": 0.14,
        "straight": 0.22,
        "prominent": 0.34,
        "convex": 0.40,
    }[
        profile.nose_profile
    ]

    points = (
        (
            -face_width
            * 0.60,
            face_height
            * 0.86,
        ),
        (
            -face_width
            * 0.83,
            0.65,
        ),
        (
            -face_width
            * 0.92,
            0.27,
        ),
        (
            -face_width
            - nose,
            -0.03,
        ),
        (
            -face_width
            * 0.93,
            -0.22,
        ),
        (
            -face_width
            * 0.78,
            -0.48,
        ),
        (
            -face_width
            * 0.56,
            -1.00,
        ),
        (
            -0.12,
            -face_height
            * 0.90,
        ),
        (
            0.45,
            -1.02,
        ),
        (
            0.76,
            -0.45,
        ),
        (
            0.82,
            0.48,
        ),
        (
            0.55,
            1.22,
        ),
        (
            0.10,
            face_height,
        ),
    )

    result.extend(
        _layered(
            "IdentityProof_Profile_Face",
            points,
            y=0.0,
            fill=palette[
                "skin"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.035,
        )
    )

    result.extend(
        _profile_hair(
            profile,
            palette,
        )
    )

    result.extend(
        _profile_facial_hair(
            profile,
            palette,
        )
    )

    result.extend(
        _layered(
            "IdentityProof_Profile_Eye",
            _almond(
                -0.61,
                0.45,
                0.46,
                0.16,
            ),
            y=-0.09,
            fill=palette[
                "eye_white"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.07,
        )
    )

    result.append(
        _ellipse(
            "IdentityProof_Profile_Iris",
            -0.63,
            0.45,
            0.075,
            0.115,
            y=-0.12,
            material=palette[
                "eye"
            ],
            count=14,
        )
    )

    return result


def _full_body(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
) -> list[
    bpy.types.Object
]:
    result: list[
        bpy.types.Object
    ] = []

    head_radius = (
        0.38
        * profile.head_scale
    )

    shoulder = {
        "slim": 0.70,
        "average": 0.82,
        "athletic": 0.94,
        "broad": 1.05,
    }[
        profile.body_silhouette
    ] * profile.shoulder_scale

    torso = (
        0.68
        * profile.torso_scale
    )

    result.extend(
        _layered(
            "IdentityProof_Body_Head",
            _ellipse_points(
                0.0,
                1.85,
                head_radius,
                head_radius
                * 1.15,
                18,
            ),
            y=0.0,
            fill=palette[
                "skin"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.05,
        )
    )

    result.extend(
        _full_body_hair(
            profile,
            palette,
            head_radius,
        )
    )

    if profile.facial_hair_style in {
        "short_beard",
        "full_beard",
    }:
        result.append(
            _polygon(
                "IdentityProof_Body_Beard",
                (
                    (
                        -head_radius
                        * 0.75,
                        1.78,
                    ),
                    (
                        -head_radius
                        * 0.55,
                        1.48,
                    ),
                    (
                        0.0,
                        1.34,
                    ),
                    (
                        head_radius
                        * 0.55,
                        1.48,
                    ),
                    (
                        head_radius
                        * 0.75,
                        1.78,
                    ),
                ),
                y=-0.08,
                material=palette[
                    "beard"
                ],
            )
        )

    result.extend(
        _layered(
            "IdentityProof_Body_Torso",
            (
                (
                    -shoulder,
                    1.30,
                ),
                (
                    -torso,
                    0.10,
                ),
                (
                    -0.50,
                    -0.70,
                ),
                (
                    0.50,
                    -0.70,
                ),
                (
                    torso,
                    0.10,
                ),
                (
                    shoulder,
                    1.30,
                ),
            ),
            y=0.06,
            fill=palette[
                "outfit"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.025,
        )
    )

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
        result.extend(
            _layered(
                (
                    "IdentityProof_Body_Arm_"
                    + side
                ),
                (
                    (
                        sign
                        * shoulder
                        * 0.90,
                        1.18,
                    ),
                    (
                        sign
                        * (
                            shoulder
                            + 0.22
                        ),
                        1.02,
                    ),
                    (
                        sign
                        * 0.90,
                        -0.55,
                    ),
                    (
                        sign
                        * 0.62,
                        -0.44,
                    ),
                ),
                y=0.02,
                fill=palette[
                    "skin"
                ],
                ink=palette[
                    "ink"
                ],
                outline=1.04,
            )
        )

    for side, x0, x1 in (
        (
            "L",
            -0.50,
            -0.04,
        ),
        (
            "R",
            0.04,
            0.50,
        ),
    ):
        result.extend(
            _layered(
                (
                    "IdentityProof_Body_Leg_"
                    + side
                ),
                (
                    (
                        x0,
                        -0.62,
                    ),
                    (
                        x1,
                        -0.62,
                    ),
                    (
                        x1,
                        -2.30,
                    ),
                    (
                        x0,
                        -2.30,
                    ),
                ),
                y=0.07,
                fill=palette[
                    "outfit"
                ],
                ink=palette[
                    "ink"
                ],
                outline=1.03,
            )
        )

    return result


def _front_face_points(
    width: float,
    height: float,
    shape: str,
) -> tuple[
    tuple[
        float,
        float,
    ],
    ...,
]:
    jaw = {
        "oval": 0.43,
        "tapered_oval": 0.34,
        "round": 0.56,
        "square": 0.62,
        "heart": 0.30,
        "long": 0.39,
    }[
        shape
    ]

    return (
        (
            -width,
            height
            * 0.78,
        ),
        (
            -width
            * 1.05,
            0.35,
        ),
        (
            -width
            * 0.92,
            -0.45,
        ),
        (
            -jaw,
            -1.12,
        ),
        (
            0.0,
            -height
            * 0.90,
        ),
        (
            jaw,
            -1.12,
        ),
        (
            width
            * 0.92,
            -0.45,
        ),
        (
            width
            * 1.05,
            0.35,
        ),
        (
            width,
            height
            * 0.78,
        ),
        (
            width
            * 0.48,
            height,
        ),
        (
            -width
            * 0.48,
            height,
        ),
    )


def _hair_volume(
    profile: PersonalAnimeCaptureProfile,
) -> float:
    return {
        "cropped": 0.15,
        "short": 0.26,
        "medium": 0.38,
        "high_volume": 0.58,
        "swept": 0.44,
    }[
        profile.hair_shape
    ]


def _front_hair(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
    face_width: float,
) -> list[
    bpy.types.Object
]:
    volume = _hair_volume(
        profile
    )

    wave = {
        "straight": 0.04,
        "wavy": 0.15,
        "curly": 0.23,
        "coily": 0.30,
    }[
        profile.hair_texture
    ]

    result: list[
        bpy.types.Object
    ] = []

    back = (
        (
            -face_width
            * 1.08,
            1.13,
        ),
        (
            -face_width
            * 0.85,
            1.65
            + volume,
        ),
        (
            -0.35,
            1.88
            + volume,
        ),
        (
            0.30,
            1.90
            + volume,
        ),
        (
            face_width
            * 0.84,
            1.64
            + volume,
        ),
        (
            face_width
            * 1.07,
            1.10,
        ),
        (
            face_width
            * 0.88,
            0.77,
        ),
        (
            -face_width
            * 0.88,
            0.77,
        ),
    )

    result.extend(
        _layered(
            "IdentityProof_Front_Hair",
            back,
            y=-0.19,
            fill=palette[
                "hair"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.035,
        )
    )

    if profile.hair_shape not in {
        "cropped",
        "short",
    }:
        for index, x in enumerate(
            (
                -0.62,
                -0.20,
                0.22,
                0.60,
            ),
            start=1,
        ):
            result.append(
                _polygon(
                    (
                        "IdentityProof_HairClump_"
                        + str(index)
                    ),
                    (
                        (
                            x - 0.25,
                            1.58
                            + volume
                            * 0.45,
                        ),
                        (
                            x,
                            1.90
                            + volume
                            + wave,
                        ),
                        (
                            x + 0.25,
                            1.58
                            + volume
                            * 0.50,
                        ),
                        (
                            x + 0.08,
                            1.12
                            + wave,
                        ),
                    ),
                    y=-0.22,
                    material=palette[
                        "hair"
                    ],
                )
            )

    return result


def _front_facial_hair(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
    face_width: float,
) -> list[
    bpy.types.Object
]:
    style = (
        profile.facial_hair_style
    )

    if style == "none":
        return []

    result: list[
        bpy.types.Object
    ] = []

    if style in {
        "moustache",
        "short_beard",
        "full_beard",
    }:
        result.append(
            _polygon(
                "IdentityProof_Moustache",
                (
                    (
                        -0.34,
                        -0.30,
                    ),
                    (
                        -0.05,
                        -0.23,
                    ),
                    (
                        0.0,
                        -0.29,
                    ),
                    (
                        0.05,
                        -0.23,
                    ),
                    (
                        0.34,
                        -0.30,
                    ),
                    (
                        0.24,
                        -0.42,
                    ),
                    (
                        0.0,
                        -0.38,
                    ),
                    (
                        -0.24,
                        -0.42,
                    ),
                ),
                y=-0.18,
                material=palette[
                    "beard"
                ],
            )
        )

    if style in {
        "short_beard",
        "full_beard",
    }:
        depth = (
            1.27
            if style
            == "full_beard"
            else 1.05
        )

        result.append(
            _polygon(
                "IdentityProof_Beard",
                (
                    (
                        -face_width
                        * 0.82,
                        -0.25,
                    ),
                    (
                        -face_width
                        * 0.68,
                        -0.75,
                    ),
                    (
                        -0.32,
                        -1.08,
                    ),
                    (
                        0.0,
                        -depth,
                    ),
                    (
                        0.32,
                        -1.08,
                    ),
                    (
                        face_width
                        * 0.68,
                        -0.75,
                    ),
                    (
                        face_width
                        * 0.82,
                        -0.25,
                    ),
                    (
                        0.42,
                        -0.41,
                    ),
                    (
                        0.0,
                        -0.35,
                    ),
                    (
                        -0.42,
                        -0.41,
                    ),
                ),
                y=-0.17,
                material=palette[
                    "beard"
                ],
            )
        )

    return result


def _profile_hair(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
) -> list[
    bpy.types.Object
]:
    volume = _hair_volume(
        profile
    )

    return list(
        _layered(
            "IdentityProof_Profile_Hair",
            (
                (
                    -0.98,
                    1.22,
                ),
                (
                    -0.78,
                    1.85
                    + volume,
                ),
                (
                    -0.20,
                    2.02
                    + volume,
                ),
                (
                    0.48,
                    1.90
                    + volume,
                ),
                (
                    0.89,
                    1.50,
                ),
                (
                    0.82,
                    0.70,
                ),
                (
                    0.25,
                    0.55,
                ),
                (
                    -0.70,
                    0.73,
                ),
            ),
            y=-0.18,
            fill=palette[
                "hair"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.035,
        )
    )


def _profile_facial_hair(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
) -> list[
    bpy.types.Object
]:
    if profile.facial_hair_style == "none":
        return []

    result: list[
        bpy.types.Object
    ] = []

    if profile.facial_hair_style in {
        "short_beard",
        "full_beard",
    }:
        result.append(
            _polygon(
                "IdentityProof_Profile_Beard",
                (
                    (
                        -1.04,
                        -0.18,
                    ),
                    (
                        -0.85,
                        -0.65,
                    ),
                    (
                        -0.48,
                        -1.08,
                    ),
                    (
                        -0.10,
                        -1.30,
                    ),
                    (
                        0.32,
                        -1.08,
                    ),
                    (
                        0.56,
                        -0.55,
                    ),
                    (
                        0.42,
                        -0.26,
                    ),
                    (
                        -0.28,
                        -0.37,
                    ),
                    (
                        -0.78,
                        -0.30,
                    ),
                ),
                y=-0.17,
                material=palette[
                    "beard"
                ],
            )
        )

    return result


def _full_body_hair(
    profile: PersonalAnimeCaptureProfile,
    palette: dict[
        str,
        bpy.types.Material,
    ],
    radius: float,
) -> list[
    bpy.types.Object
]:
    volume = _hair_volume(
        profile
    ) * 0.42

    return list(
        _layered(
            "IdentityProof_Body_Hair",
            (
                (
                    -radius,
                    1.97,
                ),
                (
                    -radius
                    * 0.68,
                    2.24
                    + volume,
                ),
                (
                    0.0,
                    2.35
                    + volume,
                ),
                (
                    radius
                    * 0.78,
                    2.18
                    + volume,
                ),
                (
                    radius,
                    1.91,
                ),
                (
                    0.25,
                    1.93,
                ),
                (
                    -0.18,
                    1.90,
                ),
            ),
            y=-0.05,
            fill=palette[
                "hair"
            ],
            ink=palette[
                "ink"
            ],
            outline=1.04,
        )
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
                    len(vertices)
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


def _layered(
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
    fill: bpy.types.Material,
    ink: bpy.types.Material,
    outline: float,
) -> tuple[
    bpy.types.Object,
    bpy.types.Object,
]:
    return (
        _polygon(
            name
            + "_Ink",
            _scale_points(
                points,
                outline,
            ),
            y=y + 0.018,
            material=ink,
        ),
        _polygon(
            name,
            points,
            y=y,
            material=fill,
        ),
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
        x
        for x, _
        in points
    ) / len(points)

    cz = sum(
        z
        for _, z
        in points
    ) / len(points)

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
    count: int,
) -> bpy.types.Object:
    return _polygon(
        name,
        _ellipse_points(
            cx,
            cz,
            rx,
            rz,
            count,
        ),
        y=y,
        material=material,
    )


def _ellipse_points(
    cx: float,
    cz: float,
    rx: float,
    rz: float,
    count: int,
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
                / count
            )
            * rx,
            cz
            + math.sin(
                2.0
                * math.pi
                * index
                / count
            )
            * rz,
        )
        for index
        in range(count)
    )


def _almond(
    cx: float,
    cz: float,
    width: float,
    height: float,
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
            * 0.22,
            cz + height
            * 0.50,
        ),
        (
            cx + width
            * 0.14,
            cz + height
            * 0.48,
        ),
        (
            cx + width
            * 0.50,
            cz,
        ),
        (
            cx + width
            * 0.14,
            cz - height
            * 0.42,
        ),
        (
            cx - width
            * 0.25,
            cz - height
            * 0.40,
        ),
    )
