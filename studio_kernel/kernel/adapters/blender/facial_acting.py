"""Trusted Blender execution for Studio acting timelines."""

from __future__ import annotations

from math import radians

import bpy

from kernel.acting import (
    ActingPoseCue,
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
    pass


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

    eye_left = face[
        "Eye_L"
    ]

    eye_right = face[
        "Eye_R"
    ]

    pupil_left = face[
        "Pupil_L"
    ]

    pupil_right = face[
        "Pupil_R"
    ]

    brow_left = face[
        "Brow_L"
    ]

    brow_right = face[
        "Brow_R"
    ]

    eye_left_base = (
        eye_left.scale.copy()
    )

    eye_right_base = (
        eye_right.scale.copy()
    )

    pupil_left_base_location = (
        pupil_left.location.copy()
    )

    pupil_right_base_location = (
        pupil_right.location.copy()
    )

    pupil_left_base_scale = (
        pupil_left.scale.copy()
    )

    pupil_right_base_scale = (
        pupil_right.scale.copy()
    )

    mouth_base_location = (
        mouth.location.copy()
    )

    mouth_base_rotation_y = (
        mouth.rotation_euler[
            1
        ]
    )

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

    brow_left.rotation_mode = "XYZ"
    brow_right.rotation_mode = "XYZ"
    mouth.rotation_mode = "XYZ"

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

        eye_left.scale[
            2
        ] = (
            eye_left_base[
                2
            ]
            * cue.eye_open_left
        )

        eye_right.scale[
            2
        ] = (
            eye_right_base[
                2
            ]
            * cue.eye_open_right
        )

        eye_left.keyframe_insert(
            data_path="scale",
            frame=cue.frame,
        )

        eye_right.keyframe_insert(
            data_path="scale",
            frame=cue.frame,
        )

        for (
            pupil,
            base_location,
            base_scale,
        ) in (
            (
                pupil_left,
                pupil_left_base_location,
                pupil_left_base_scale,
            ),
            (
                pupil_right,
                pupil_right_base_location,
                pupil_right_base_scale,
            ),
        ):
            pupil.location[
                0
            ] = (
                base_location[
                    0
                ]
                + cue.pupil_x
            )

            pupil.location[
                2
            ] = (
                base_location[
                    2
                ]
                + cue.pupil_z
            )

            pupil.scale[
                0
            ] = (
                base_scale[
                    0
                ]
                * cue.pupil_scale
            )

            pupil.scale[
                2
            ] = (
                base_scale[
                    2
                ]
                * cue.pupil_scale
            )

            pupil.keyframe_insert(
                data_path="location",
                frame=cue.frame,
            )

            pupil.keyframe_insert(
                data_path="scale",
                frame=cue.frame,
            )

        mouth.rotation_euler[
            1
        ] = (
            mouth_base_rotation_y
            + radians(
                cue.mouth_tilt_degrees
            )
        )

        mouth.location[
            2
        ] = (
            mouth_base_location[
                2
            ]
            + cue.mouth_z_offset
        )

        mouth.keyframe_insert(
            data_path="rotation_euler",
            frame=cue.frame,
        )

        mouth.keyframe_insert(
            data_path="location",
            frame=cue.frame,
        )

    for cue in timeline.blinks:
        pose = _pose_at(
            timeline.poses,
            cue.frame,
        )

        if cue.closed:
            left_factor = 0.10
            right_factor = 0.10
            pupil_factor = 0.10

        else:
            left_factor = (
                pose.eye_open_left
            )
            right_factor = (
                pose.eye_open_right
            )
            pupil_factor = (
                pose.pupil_scale
            )

        eye_left.scale[
            2
        ] = (
            eye_left_base[
                2
            ]
            * left_factor
        )

        eye_right.scale[
            2
        ] = (
            eye_right_base[
                2
            ]
            * right_factor
        )

        eye_left.keyframe_insert(
            data_path="scale",
            frame=cue.frame,
        )

        eye_right.keyframe_insert(
            data_path="scale",
            frame=cue.frame,
        )

        for (
            pupil,
            base_scale,
        ) in (
            (
                pupil_left,
                pupil_left_base_scale,
            ),
            (
                pupil_right,
                pupil_right_base_scale,
            ),
        ):
            pupil.scale[
                2
            ] = (
                base_scale[
                    2
                ]
                * pupil_factor
            )

            pupil.keyframe_insert(
                data_path="scale",
                frame=cue.frame,
            )

    scene.frame_set(
        1
    )

    bpy.context.view_layer.update()


def _pose_at(
    poses: tuple[
        ActingPoseCue,
        ...,
    ],
    frame: int,
) -> ActingPoseCue:
    current = (
        poses[
            0
        ]
    )

    for pose in poses:
        if pose.frame > frame:
            break

        current = pose

    return current


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
