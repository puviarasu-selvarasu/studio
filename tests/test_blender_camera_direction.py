"""Tests for trusted Director-to-Blender camera compilation."""

from __future__ import annotations

import pytest

from kernel.adapters.blender.camera_direction import (
    CameraDirectionError,
    compile_camera_direction,
)


def test_static_medium_camera_is_deterministic() -> None:
    command = compile_camera_direction(
        framing="medium",
        camera_intent="static",
        pacing="slow",
        timeline_end_frame=192,
    )

    assert command.start_location == (
        6.5,
        -9.0,
        4.0,
    )

    assert (
        command.end_location
        == command.start_location
    )

    assert (
        command.start_target
        == command.end_target
    )

    assert command.start_frame == 1
    assert command.end_frame == 192


def test_close_up_is_nearer_than_wide() -> None:
    wide = compile_camera_direction(
        framing="wide",
        camera_intent="static",
        pacing="slow",
        timeline_end_frame=192,
    )

    close_up = compile_camera_direction(
        framing="close_up",
        camera_intent="static",
        pacing="slow",
        timeline_end_frame=192,
    )

    wide_distance = sum(
        value * value
        for value in wide.start_location
    )

    close_distance = sum(
        value * value
        for value in close_up.start_location
    )

    assert close_distance < wide_distance


def test_push_in_moves_camera_toward_target() -> None:
    command = compile_camera_direction(
        framing="medium",
        camera_intent="push_in",
        pacing="slow",
        timeline_end_frame=192,
    )

    start_distance = sum(
        (
            command.start_location[index]
            - command.start_target[index]
        ) ** 2
        for index in range(3)
    )

    end_distance = sum(
        (
            command.end_location[index]
            - command.end_target[index]
        ) ** 2
        for index in range(3)
    )

    assert end_distance < start_distance


def test_pull_back_moves_camera_away_from_target() -> None:
    command = compile_camera_direction(
        framing="medium",
        camera_intent="pull_back",
        pacing="slow",
        timeline_end_frame=192,
    )

    start_distance = sum(
        (
            command.start_location[index]
            - command.start_target[index]
        ) ** 2
        for index in range(3)
    )

    end_distance = sum(
        (
            command.end_location[index]
            - command.end_target[index]
        ) ** 2
        for index in range(3)
    )

    assert end_distance > start_distance


def test_pan_left_changes_target_not_camera_location() -> None:
    command = compile_camera_direction(
        framing="medium",
        camera_intent="pan_left",
        pacing="slow",
        timeline_end_frame=192,
    )

    assert (
        command.start_location
        == command.end_location
    )

    assert (
        command.start_target
        != command.end_target
    )

    assert (
        command.end_target[0]
        < command.start_target[0]
    )


def test_pan_right_changes_target_not_camera_location() -> None:
    command = compile_camera_direction(
        framing="medium",
        camera_intent="pan_right",
        pacing="slow",
        timeline_end_frame=192,
    )

    assert (
        command.start_location
        == command.end_location
    )

    assert (
        command.end_target[0]
        > command.start_target[0]
    )


@pytest.mark.parametrize(
    (
        "pacing",
        "expected_end",
    ),
    (
        (
            "slow",
            192,
        ),
        (
            "moderate",
            144,
        ),
        (
            "fast",
            96,
        ),
    ),
)
def test_pacing_controls_camera_motion_window(
    pacing: str,
    expected_end: int,
) -> None:
    command = compile_camera_direction(
        framing="medium",
        camera_intent="push_in",
        pacing=pacing,
        timeline_end_frame=192,
    )

    assert command.end_frame == expected_end


@pytest.mark.parametrize(
    (
        "field",
        "value",
        "message",
    ),
    (
        (
            "framing",
            "extreme_random_angle",
            "framing",
        ),
        (
            "camera_intent",
            "teleport",
            "camera intent",
        ),
        (
            "pacing",
            "chaotic",
            "pacing",
        ),
    ),
)
def test_invalid_director_camera_values_are_rejected(
    field: str,
    value: str,
    message: str,
) -> None:
    kwargs = {
        "framing": "medium",
        "camera_intent": "static",
        "pacing": "slow",
        "timeline_end_frame": 192,
    }

    kwargs[field] = value

    with pytest.raises(
        CameraDirectionError,
        match=message,
    ):
        compile_camera_direction(
            **kwargs
        )


def test_invalid_timeline_is_rejected() -> None:
    with pytest.raises(
        CameraDirectionError,
        match="Timeline",
    ):
        compile_camera_direction(
            framing="medium",
            camera_intent="static",
            pacing="slow",
            timeline_end_frame=0,
        )
