"""Validation rules for Studio Animation IR."""

from __future__ import annotations

from dataclasses import dataclass

from .models import AnimationScene


@dataclass(frozen=True)
class ValidationError:
    """Represent one Animation IR validation failure."""

    field: str
    message: str


def validate_animation_scene(
    scene: AnimationScene,
) -> list[ValidationError]:
    """Validate basic structural rules for an animation scene.

    Args:
        scene: Animation scene to validate.

    Returns:
        List of validation errors. An empty list means the scene is valid.
    """
    errors: list[ValidationError] = []

    if not scene.scene_id.strip():
        errors.append(
            ValidationError(
                field="scene_id",
                message="Scene ID must not be empty.",
            )
        )

    if scene.duration_seconds <= 0:
        errors.append(
            ValidationError(
                field="duration_seconds",
                message="Scene duration must be greater than zero.",
            )
        )

    for character_index, character in enumerate(scene.characters):
        if not character.character_id.strip():
            errors.append(
                ValidationError(
                    field=f"characters[{character_index}].character_id",
                    message="Character ID must not be empty.",
                )
            )

        for action_index, action in enumerate(character.actions):
            field_prefix = (
                f"characters[{character_index}]."
                f"actions[{action_index}]"
            )

            if not action.action.strip():
                errors.append(
                    ValidationError(
                        field=f"{field_prefix}.action",
                        message="Action name must not be empty.",
                    )
                )

            if action.start_seconds < 0:
                errors.append(
                    ValidationError(
                        field=f"{field_prefix}.start_seconds",
                        message="Action start time cannot be negative.",
                    )
                )

            if action.duration_seconds <= 0:
                errors.append(
                    ValidationError(
                        field=f"{field_prefix}.duration_seconds",
                        message="Action duration must be greater than zero.",
                    )
                )

            action_end = (
                action.start_seconds + action.duration_seconds
            )

            if action_end > scene.duration_seconds:
                errors.append(
                    ValidationError(
                        field=field_prefix,
                        message=(
                            "Action extends beyond the scene duration."
                        ),
                    )
                )

    return errors
