"""Validated AI-facing contract for Studio Animator plans."""

from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError as PydanticValidationError,
    model_validator,
)

from kernel.animation_ir.models import (
    AnimationAction,
    AnimationScene,
    CharacterAnimation,
)
from kernel.animation_ir.validator import (
    validate_animation_scene,
)


class AnimatorPlanParseError(Exception):
    """Represent invalid Animator JSON returned by an AI model."""


class AnimatorPlanConversionError(Exception):
    """Represent failure to convert a plan into trusted Animation IR."""


class AnimatorActionPlan(BaseModel):
    """Describe one AI-planned semantic character action."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )

    action: str = Field(
        min_length=1,
    )

    start_seconds: float = Field(
        ge=0.0,
    )

    duration_seconds: float = Field(
        gt=0.0,
    )


class AnimatorPlan(BaseModel):
    """Describe one validated single-character Animator plan."""

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

    actions: tuple[
        AnimatorActionPlan,
        ...
    ] = Field(
        min_length=1,
    )

    @model_validator(mode="after")
    def validate_action_bounds(
        self,
    ) -> "AnimatorPlan":
        """Require every action to fit inside the scene."""

        for index, action in enumerate(self.actions):
            action_end = (
                action.start_seconds
                + action.duration_seconds
            )

            if action_end > self.duration_seconds:
                raise ValueError(
                    f"actions[{index}] extends beyond "
                    "scene duration."
                )

        return self


def animator_plan_from_json(
    raw_json: str,
) -> AnimatorPlan:
    """Parse and validate raw AI JSON into an Animator plan."""

    if not raw_json.strip():
        raise AnimatorPlanParseError(
            "Animator plan JSON must not be empty."
        )

    try:
        return AnimatorPlan.model_validate_json(
            raw_json
        )
    except PydanticValidationError as exc:
        raise AnimatorPlanParseError(
            f"Invalid Animator plan JSON: {exc}"
        ) from exc


def animation_scene_from_plan(
    plan: AnimatorPlan,
) -> AnimationScene:
    """Convert an AI-facing plan into trusted Animation IR."""

    scene = AnimationScene(
        scene_id=plan.scene_id,
        duration_seconds=plan.duration_seconds,
        characters=(
            CharacterAnimation(
                character_id=plan.character_id,
                actions=tuple(
                    AnimationAction(
                        action=action.action,
                        start_seconds=action.start_seconds,
                        duration_seconds=action.duration_seconds,
                    )
                    for action in plan.actions
                ),
            ),
        ),
    )

    errors = validate_animation_scene(
        scene
    )

    if errors:
        details = "; ".join(
            f"{error.field}: {error.message}"
            for error in errors
        )

        raise AnimatorPlanConversionError(
            "Animator plan produced invalid "
            f"Animation IR: {details}"
        )

    return scene