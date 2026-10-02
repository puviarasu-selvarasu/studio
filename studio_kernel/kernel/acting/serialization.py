"""Strict JSON boundary for Studio acting timelines."""

from __future__ import annotations

import json
from typing import Any

from kernel.acting.models import (
    ActingDomainError,
    ActingPoseCue,
    ActingTimeline,
    BlinkCue,
    Viseme,
    VisemeCue,
)


ACTING_TIMELINE_SCHEMA_VERSION = 1


class ActingTimelineParseError(
    ActingDomainError
):
    pass


_POSE_KEYS = {
    "frame",
    "head_pitch_degrees",
    "head_yaw_degrees",
    "head_roll_degrees",
    "chest_pitch_degrees",
    "brow_left_degrees",
    "brow_right_degrees",
    "eye_open_left",
    "eye_open_right",
    "pupil_x",
    "pupil_z",
    "pupil_scale",
    "mouth_tilt_degrees",
    "mouth_z_offset",
}


def acting_timeline_to_data(
    timeline: ActingTimeline,
) -> dict[str, object]:
    return {
        "schema_version": (
            ACTING_TIMELINE_SCHEMA_VERSION
        ),
        "fps": timeline.fps,
        "end_frame": timeline.end_frame,
        "visemes": [
            {
                "frame": cue.frame,
                "viseme": (
                    cue.viseme.value
                ),
                "strength": (
                    cue.strength
                ),
            }
            for cue
            in timeline.visemes
        ],
        "blinks": [
            {
                "frame": cue.frame,
                "closed": cue.closed,
            }
            for cue
            in timeline.blinks
        ],
        "poses": [
            {
                "frame": cue.frame,
                "head_pitch_degrees": cue.head_pitch_degrees,
                "head_yaw_degrees": cue.head_yaw_degrees,
                "head_roll_degrees": cue.head_roll_degrees,
                "chest_pitch_degrees": cue.chest_pitch_degrees,
                "brow_left_degrees": cue.brow_left_degrees,
                "brow_right_degrees": cue.brow_right_degrees,
                "eye_open_left": cue.eye_open_left,
                "eye_open_right": cue.eye_open_right,
                "pupil_x": cue.pupil_x,
                "pupil_z": cue.pupil_z,
                "pupil_scale": cue.pupil_scale,
                "mouth_tilt_degrees": cue.mouth_tilt_degrees,
                "mouth_z_offset": cue.mouth_z_offset,
            }
            for cue
            in timeline.poses
        ],
    }


def acting_timeline_to_json(
    timeline: ActingTimeline,
) -> str:
    return (
        json.dumps(
            acting_timeline_to_data(
                timeline
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def acting_timeline_from_json(
    raw: str,
) -> ActingTimeline:
    try:
        data = json.loads(
            raw
        )
    except json.JSONDecodeError as exc:
        raise ActingTimelineParseError(
            "Acting timeline is not valid JSON."
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise ActingTimelineParseError(
            "Acting timeline must be an object."
        )

    expected = {
        "schema_version",
        "fps",
        "end_frame",
        "visemes",
        "blinks",
        "poses",
    }

    if set(
        data.keys()
    ) != expected:
        raise ActingTimelineParseError(
            "Acting timeline keys are invalid."
        )

    if (
        data[
            "schema_version"
        ]
        != ACTING_TIMELINE_SCHEMA_VERSION
    ):
        raise ActingTimelineParseError(
            "Unsupported acting timeline schema."
        )

    try:
        visemes = tuple(
            VisemeCue(
                frame=int(
                    item[
                        "frame"
                    ]
                ),
                viseme=Viseme(
                    item[
                        "viseme"
                    ]
                ),
                strength=float(
                    item[
                        "strength"
                    ]
                ),
            )
            for item
            in _records(
                data[
                    "visemes"
                ],
                {
                    "frame",
                    "viseme",
                    "strength",
                },
                "visemes",
            )
        )

        blinks = tuple(
            BlinkCue(
                frame=int(
                    item[
                        "frame"
                    ]
                ),
                closed=_strict_bool(
                    item[
                        "closed"
                    ]
                ),
            )
            for item
            in _records(
                data[
                    "blinks"
                ],
                {
                    "frame",
                    "closed",
                },
                "blinks",
            )
        )

        poses = tuple(
            ActingPoseCue(
                frame=int(
                    item[
                        "frame"
                    ]
                ),
                head_pitch_degrees=float(
                    item[
                        "head_pitch_degrees"
                    ]
                ),
                head_yaw_degrees=float(
                    item[
                        "head_yaw_degrees"
                    ]
                ),
                head_roll_degrees=float(
                    item[
                        "head_roll_degrees"
                    ]
                ),
                chest_pitch_degrees=float(
                    item[
                        "chest_pitch_degrees"
                    ]
                ),
                brow_left_degrees=float(
                    item[
                        "brow_left_degrees"
                    ]
                ),
                brow_right_degrees=float(
                    item[
                        "brow_right_degrees"
                    ]
                ),
                eye_open_left=float(
                    item[
                        "eye_open_left"
                    ]
                ),
                eye_open_right=float(
                    item[
                        "eye_open_right"
                    ]
                ),
                pupil_x=float(
                    item[
                        "pupil_x"
                    ]
                ),
                pupil_z=float(
                    item[
                        "pupil_z"
                    ]
                ),
                pupil_scale=float(
                    item[
                        "pupil_scale"
                    ]
                ),
                mouth_tilt_degrees=float(
                    item[
                        "mouth_tilt_degrees"
                    ]
                ),
                mouth_z_offset=float(
                    item[
                        "mouth_z_offset"
                    ]
                ),
            )
            for item
            in _records(
                data[
                    "poses"
                ],
                _POSE_KEYS,
                "poses",
            )
        )

        return ActingTimeline(
            fps=int(
                data[
                    "fps"
                ]
            ),
            end_frame=int(
                data[
                    "end_frame"
                ]
            ),
            visemes=visemes,
            blinks=blinks,
            poses=poses,
        )

    except (
        KeyError,
        TypeError,
        ValueError,
        ActingDomainError,
    ) as exc:
        raise ActingTimelineParseError(
            "Invalid acting timeline data."
        ) from exc


def _records(
    value: Any,
    keys: set[str],
    label: str,
) -> tuple[
    dict[str, Any],
    ...,
]:
    if not isinstance(
        value,
        list,
    ):
        raise ActingTimelineParseError(
            label
            + " must be a list."
        )

    records = []

    for item in value:
        if (
            not isinstance(
                item,
                dict,
            )
            or set(
                item.keys()
            )
            != keys
        ):
            raise ActingTimelineParseError(
                label
                + " contains an invalid record."
            )

        records.append(
            item
        )

    return tuple(
        records
    )


def _strict_bool(
    value: Any,
) -> bool:
    if not isinstance(
        value,
        bool,
    ):
        raise ActingTimelineParseError(
            "closed must be boolean."
        )

    return value
