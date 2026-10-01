"""Tests for Studio Director plan contracts."""

from __future__ import annotations

import json

import pytest

from kernel.application.director_plan import (
    DirectorPlanParseError,
    director_plan_from_json,
)


def _valid_plan_json() -> str:
    return json.dumps(
        {
            "scene_id": "director_scene_1",
            "duration_seconds": 8.0,
            "character_id": "momo",
            "scene_objective": (
                "Show Momo recognizing an old friend."
            ),
            "emotion": (
                "uncertainty to warm recognition"
            ),
            "shot": {
                "framing": "medium",
                "camera_intent": "push_in",
                "pacing": "slow",
            },
            "performance_intent": (
                "Momo notices the person, hesitates, "
                "recognizes them, greets them, then "
                "approaches cautiously."
            ),
        }
    )


def test_director_plan_parses_valid_json() -> None:
    plan = director_plan_from_json(
        _valid_plan_json()
    )

    assert plan.scene_id == "director_scene_1"
    assert plan.duration_seconds == 8.0
    assert plan.character_id == "momo"

    assert (
        plan.scene_objective
        == "Show Momo recognizing an old friend."
    )

    assert (
        plan.emotion
        == "uncertainty to warm recognition"
    )

    assert plan.shot.framing == "medium"
    assert plan.shot.camera_intent == "push_in"
    assert plan.shot.pacing == "slow"

    assert "hesitates" in plan.performance_intent


def test_director_plan_is_frozen() -> None:
    plan = director_plan_from_json(
        _valid_plan_json()
    )

    with pytest.raises(
        Exception
    ):
        plan.scene_id = "changed"


def test_director_plan_rejects_empty_json() -> None:
    with pytest.raises(
        DirectorPlanParseError,
        match="must not be empty",
    ):
        director_plan_from_json(
            "   "
        )


def test_director_plan_rejects_extra_root_field() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["unsafe"] = "extra"

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )


def test_director_plan_rejects_extra_shot_field() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["shot"]["unsafe"] = "extra"

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )


def test_director_plan_rejects_invalid_framing() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["shot"]["framing"] = "extreme_random_angle"

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )


def test_director_plan_rejects_invalid_camera_intent() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["shot"]["camera_intent"] = "teleport_camera"

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )


def test_director_plan_rejects_invalid_pacing() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["shot"]["pacing"] = "chaotic"

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )


def test_director_plan_rejects_zero_duration() -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data["duration_seconds"] = 0.0

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )


@pytest.mark.parametrize(
    "field",
    (
        "scene_id",
        "character_id",
        "scene_objective",
        "emotion",
        "performance_intent",
    ),
)
def test_director_plan_rejects_blank_required_text(
    field: str,
) -> None:
    data = json.loads(
        _valid_plan_json()
    )

    data[field] = "   "

    with pytest.raises(
        DirectorPlanParseError
    ):
        director_plan_from_json(
            json.dumps(data)
        )
