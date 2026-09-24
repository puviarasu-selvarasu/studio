"""Validation rules for Studio content."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Lesson


@dataclass(frozen=True)
class ContentValidationError:
    """Represent one content validation failure."""

    field: str
    message: str


def validate_lesson(lesson: Lesson) -> list[ContentValidationError]:
    """Validate the structural requirements of a lesson.

    Args:
        lesson: Lesson to validate.

    Returns:
        List of validation errors.
    """
    errors: list[ContentValidationError] = []

    if not lesson.title.strip():
        errors.append(
            ContentValidationError(
                field="title",
                message="Lesson title must not be empty.",
            )
        )

    if not lesson.topic.strip():
        errors.append(
            ContentValidationError(
                field="topic",
                message="Lesson topic must not be empty.",
            )
        )

    if lesson.target_age <= 0:
        errors.append(
            ContentValidationError(
                field="target_age",
                message="Target age must be greater than zero.",
            )
        )

    if not lesson.language.strip():
        errors.append(
            ContentValidationError(
                field="language",
                message="Language must not be empty.",
            )
        )

    if not lesson.scenes:
        errors.append(
            ContentValidationError(
                field="scenes",
                message="Lesson must contain at least one scene.",
            )
        )

    for index, scene in enumerate(lesson.scenes):
        prefix = f"scenes[{index}]"

        if not scene.scene_id.strip():
            errors.append(
                ContentValidationError(
                    field=f"{prefix}.scene_id",
                    message="Scene ID must not be empty.",
                )
            )

        if not scene.narration.strip():
            errors.append(
                ContentValidationError(
                    field=f"{prefix}.narration",
                    message="Narration must not be empty.",
                )
            )

        if not scene.visual_description.strip():
            errors.append(
                ContentValidationError(
                    field=f"{prefix}.visual_description",
                    message="Visual description must not be empty.",
                )
            )

        if scene.duration_seconds <= 0:
            errors.append(
                ContentValidationError(
                    field=f"{prefix}.duration_seconds",
                    message="Scene duration must be greater than zero.",
                )
            )

    return errors
