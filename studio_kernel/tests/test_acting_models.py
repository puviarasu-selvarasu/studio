"""Tests for Studio acting-domain contracts."""

from __future__ import annotations

import json

import pytest

from kernel.acting import (
    ActingDomainError,
    ActingPoseCue,
    ActingTimeline,
    BlinkCue,
    Viseme,
    VisemeCue,
    acting_timeline_from_json,
    acting_timeline_to_json,
)


def _timeline() -> ActingTimeline:
    return ActingTimeline(
        fps=24,
        end_frame=24,
        visemes=(
            VisemeCue(
                frame=1,
                viseme=Viseme.REST,
                strength=0.0,
            ),
            VisemeCue(
                frame=5,
                viseme=Viseme.OPEN,
                strength=0.7,
            ),
            VisemeCue(
                frame=24,
                viseme=Viseme.REST,
                strength=0.0,
            ),
        ),
        blinks=(
            BlinkCue(
                frame=8,
                closed=True,
            ),
            BlinkCue(
                frame=10,
                closed=False,
            ),
        ),
        poses=(
            ActingPoseCue(
                frame=1,
            ),
            ActingPoseCue(
                frame=12,
                head_yaw_degrees=4.0,
                brow_left_degrees=-6.0,
                brow_right_degrees=6.0,
            ),
            ActingPoseCue(
                frame=24,
            ),
        ),
    )


def test_acting_timeline_round_trips_strict_json() -> None:
    timeline = (
        _timeline()
    )

    loaded = (
        acting_timeline_from_json(
            acting_timeline_to_json(
                timeline
            )
        )
    )

    assert loaded == timeline


def test_viseme_strength_is_bounded() -> None:
    with pytest.raises(
        ActingDomainError
    ):
        VisemeCue(
            frame=1,
            viseme=Viseme.OPEN,
            strength=1.5,
        )


def test_timeline_rejects_duplicate_viseme_frames() -> None:
    with pytest.raises(
        ActingDomainError,
        match="duplicate",
    ):
        ActingTimeline(
            fps=24,
            end_frame=10,
            visemes=(
                VisemeCue(
                    frame=1,
                    viseme=Viseme.REST,
                    strength=0.0,
                ),
                VisemeCue(
                    frame=1,
                    viseme=Viseme.OPEN,
                    strength=0.5,
                ),
            ),
            blinks=(),
            poses=(
                ActingPoseCue(
                    frame=1,
                ),
            ),
        )


def test_parser_rejects_extra_animation_ir_like_field() -> None:
    data = json.loads(
        acting_timeline_to_json(
            _timeline()
        )
    )

    data[
        "character_variant"
    ] = "default"

    with pytest.raises(
        ActingDomainError
    ):
        acting_timeline_from_json(
            json.dumps(
                data
            )
        )
