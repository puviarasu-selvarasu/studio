"""Trusted Blender execution for Studio acting timelines."""

from __future__ import annotations

from math import radians

import bpy

from kernel.acting import (
    ActingTimeline,
    Viseme,
)
from kernel.adapters.blender.character_builder import (
    BuiltCharacter,
)
from kernel.adapters.blender.pose_controls import (
    insert_bone_rotation_keyframe,
    set_bone_rotation_degrees,
)


class FacialActingError(
    RuntimeError
):
    """Raised when canonical facial acting cannot be executed."""


_MOUTH_SCALES = {
    Viseme.REST: (
        1.00,
        1.00,
    ),

    Viseme.CLOSED: (
        1.05,
        0.40,
    ),

    Viseme.OPEN: (
        0.90,
        2.10,
    ),

    Viseme.WIDE: (
        1.45,
        1.35,
    ),

    Viseme.ROUND: (
        0.66,
        2.00,
    ),
}


def apply_acting_timeline(
    built_character: BuiltCharacter,
    timeline: ActingTimeline,
) -> None:
    """Apply only trusted acting data to the canonical production character."""

    face = _face_parts(
        built_character
    )

    rig = (
        built_character.armature
    )

    scene = bpy.context.scene

    scene.frame_start = 1
    scene.frame_end = (
        timeline.end_frame
    )

    scene.render.fps = (
        timeline.fps
    )

    mouth = face[
        "Mouth"
    ]

    for cue in timeline.visemes:
        width_scale, height_scale = (
            _MOUTH_SCALES[
                cue.viseme
            ]
        )

        strength = (
            cue.strength
        )

        mouth.scale[0] = (
            1.0
            + (
                width_scale
                - 1.0
            )
            * strength
        )

        mouth.scale[1] = 1.0

        mouth.scale[2] = (
            1.0
            + (
                height_scale
                - 1.0
            )
            * max(
                0.35,
                strength,
            )
            if cue.viseme
            is not Viseme.REST
            else 1.0
        )

        mouth.keyframe_insert(
            data_path="scale",
            frame=cue.frame,
        )

    blink_parts = (
        face[
            "Eye_L"
        ],
        face[
            "Eye_R"
        ],
        face[
            "Pupil_L"
        ],
        face[
            "Pupil_R"
        ],
    )

    for cue in timeline.blinks:
        z_scale = (
            0.10
            if cue.closed
            else 1.0
        )

        for obj in blink_parts:
            obj.scale[2] = (
                z_scale
            )

            obj.keyframe_insert(
                data_path="scale",
                frame=cue.frame,
            )

    brow_left = face[
        "Brow_L"
    ]

    brow_right = face[
        "Brow_R"
    ]

    brow_left.rotation_mode = (
        "XYZ"
    )

    brow_right.rotation_mode = (
        "XYZ"
    )

    for cue in timeline.poses:
        set_bone_rotation_degrees(
            rig.name,
            "head",
            (
                cue.head_pitch_degrees,
                cue.head_yaw_degrees,
                cue.head_roll_degrees,
            ),
        )

        insert_bone_rotation_keyframe(
            rig.name,
            "head",
            cue.frame,
        )

        set_bone_rotation_degrees(
            rig.name,
            "chest",
            (
                cue.chest_pitch_degrees,
                0.0,
                0.0,
            ),
        )

        insert_bone_rotation_keyframe(
            rig.name,
            "chest",
            cue.frame,
        )

        brow_left.rotation_euler[
            1
        ] = radians(
            cue.brow_left_degrees
        )

        brow_right.rotation_euler[
            1
        ] = radians(
            cue.brow_right_degrees
        )

        brow_left.keyframe_insert(
            data_path="rotation_euler",
            frame=cue.frame,
        )

        brow_right.keyframe_insert(
            data_path="rotation_euler",
            frame=cue.frame,
        )

    scene.frame_set(
        1
    )

    bpy.context.view_layer.update()


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

    result: dict[
        str,
        bpy.types.Object,
    ] = {}

    marker = (
        prefix
        + "_Face_"
    )

    for obj in (
        built_character.face_parts
    ):
        if not obj.name.startswith(
            marker
        ):
            continue

        label = obj.name[
            len(
                marker
            ):
        ]

        result[
            label
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
        - set(
            result
        )
    )

    if missing:
        raise FacialActingError(
            "Canonical face is missing: "
            + ", ".join(
                sorted(
                    missing
                )
            )
        )

    return result
