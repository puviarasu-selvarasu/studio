"""Compile validated Director shot intent into trusted camera commands.

This module contains no Blender or AI execution. It translates Studio's
bounded Director shot vocabulary into deterministic camera geometry that a
trusted Blender-side executor may later apply.
"""

from __future__ import annotations

from dataclasses import dataclass


Vector3 = tuple[
    float,
    float,
    float,
]


class CameraDirectionError(ValueError):
    """Represent unsupported Director camera direction."""


@dataclass(frozen=True, slots=True)
class CameraDirectionCommand:
    """Describe one trusted deterministic camera movement."""

    framing: str
    camera_intent: str
    pacing: str

    start_location: Vector3
    end_location: Vector3

    start_target: Vector3
    end_target: Vector3

    start_frame: int
    end_frame: int


_FRAMING_LOCATIONS: dict[
    str,
    Vector3,
] = {
    "wide": (
        8.0,
        -11.0,
        4.8,
    ),
    "medium": (
        6.5,
        -9.0,
        4.0,
    ),
    "close_up": (
        4.7,
        -6.5,
        3.2,
    ),
}


_TARGET: Vector3 = (
    0.0,
    -0.4,
    1.0,
)


_PACING_FRACTIONS: dict[
    str,
    float,
] = {
    "slow": 1.0,
    "moderate": 0.75,
    "fast": 0.5,
}


def _move_toward(
    start: Vector3,
    target: Vector3,
    fraction: float,
) -> Vector3:
    """Move a location a bounded fraction toward the target."""

    return tuple(
        start[index]
        + (
            target[index]
            - start[index]
        )
        * fraction
        for index in range(3)
    )


def _move_away(
    start: Vector3,
    target: Vector3,
    fraction: float,
) -> Vector3:
    """Move a location a bounded fraction away from the target."""

    return tuple(
        start[index]
        + (
            start[index]
            - target[index]
        )
        * fraction
        for index in range(3)
    )


def compile_camera_direction(
    *,
    framing: str,
    camera_intent: str,
    pacing: str,
    timeline_end_frame: int,
) -> CameraDirectionCommand:
    """Compile bounded Director camera intent into deterministic geometry."""

    if timeline_end_frame < 1:
        raise CameraDirectionError(
            "Timeline end frame must be greater than or equal to 1."
        )

    if framing not in _FRAMING_LOCATIONS:
        raise CameraDirectionError(
            f"Unsupported framing: {framing}"
        )

    supported_intents = {
        "static",
        "push_in",
        "pull_back",
        "pan_left",
        "pan_right",
    }

    if camera_intent not in supported_intents:
        raise CameraDirectionError(
            f"Unsupported camera intent: {camera_intent}"
        )

    if pacing not in _PACING_FRACTIONS:
        raise CameraDirectionError(
            f"Unsupported pacing: {pacing}"
        )

    start_location = _FRAMING_LOCATIONS[
        framing
    ]

    end_location = start_location

    start_target = _TARGET
    end_target = _TARGET

    if camera_intent == "push_in":
        end_location = _move_toward(
            start_location,
            _TARGET,
            0.20,
        )

    elif camera_intent == "pull_back":
        end_location = _move_away(
            start_location,
            _TARGET,
            0.18,
        )

    elif camera_intent == "pan_left":
        start_target = (
            0.65,
            _TARGET[1],
            _TARGET[2],
        )

        end_target = (
            -0.65,
            _TARGET[1],
            _TARGET[2],
        )

    elif camera_intent == "pan_right":
        start_target = (
            -0.65,
            _TARGET[1],
            _TARGET[2],
        )

        end_target = (
            0.65,
            _TARGET[1],
            _TARGET[2],
        )

    fraction = _PACING_FRACTIONS[
        pacing
    ]

    movement_end_frame = max(
        1,
        round(
            timeline_end_frame
            * fraction
        ),
    )

    return CameraDirectionCommand(
        framing=framing,
        camera_intent=camera_intent,
        pacing=pacing,
        start_location=start_location,
        end_location=end_location,
        start_target=start_target,
        end_target=end_target,
        start_frame=1,
        end_frame=movement_end_frame,
    )
