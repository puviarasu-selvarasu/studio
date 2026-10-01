"""Validated AI-facing contract for Studio Director plans."""

from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError as PydanticValidationError,
)


class DirectorPlanParseError(Exception):
    """Represent invalid Director JSON returned by an AI model."""


class DirectorShotPlan(BaseModel):
    """Describe one intentionally narrow single-shot direction."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    framing: Literal[
        "wide",
        "medium",
        "close_up",
    ]

    camera_intent: Literal[
        "static",
        "push_in",
        "pull_back",
        "pan_left",
        "pan_right",
    ]

    pacing: Literal[
        "slow",
        "moderate",
        "fast",
    ]


class DirectorPlan(BaseModel):
    """Describe one validated single-character Director plan."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    scene_id: str = Field(
        min_length=1,
    )

    duration_seconds: float = Field(
        gt=0.0,
    )

    character_id: str = Field(
        min_length=1,
    )

    scene_objective: str = Field(
        min_length=1,
    )

    emotion: str = Field(
        min_length=1,
    )

    shot: DirectorShotPlan

    performance_intent: str = Field(
        min_length=1,
    )


def director_plan_from_json(
    raw_json: str,
) -> DirectorPlan:
    """Parse and validate raw AI JSON into a Director plan."""

    if not raw_json.strip():
        raise DirectorPlanParseError(
            "Director plan JSON must not be empty."
        )

    try:
        return DirectorPlan.model_validate_json(
            raw_json
        )
    except PydanticValidationError as exc:
        raise DirectorPlanParseError(
            f"Invalid Director plan JSON: {exc}"
        ) from exc
