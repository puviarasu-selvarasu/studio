"""JSON serialization boundary for Studio content."""

from __future__ import annotations

import json
import math

from typing import Any

from .models import ContentScene, Lesson
from .validator import validate_lesson


class ContentParseError(Exception):
    """Represent a failure while converting JSON into content models."""

    def __init__(self, message: str) -> None:
        """Initialize the parsing error."""
        super().__init__(message)
        self.message = message


def lesson_from_json(json_text: str) -> Lesson:
    """Parse JSON text into a validated Lesson domain object.

    Args:
        json_text: JSON document representing a lesson.

    Returns:
        A structurally valid Lesson.

    Raises:
        ContentParseError: If the JSON cannot be converted into a valid Lesson.
    """
    try:
        raw_data = json.loads(json_text.lstrip("\ufeff"))
    except json.JSONDecodeError as exc:
        raise ContentParseError(
            f"Invalid JSON: {exc.msg} at position {exc.pos}."
        ) from exc

    if not isinstance(raw_data, dict):
        raise ContentParseError("Lesson JSON root must be an object.")

    title = _require_string(raw_data, "title")
    topic = _require_string(raw_data, "topic")
    target_age = _require_integer(raw_data, "target_age")
    language = _require_string(raw_data, "language")
    raw_scenes = raw_data.get("scenes")

    if not isinstance(raw_scenes, list):
        raise ContentParseError("Field 'scenes' must be an array.")

    scenes: list[ContentScene] = []

    for index, raw_scene in enumerate(raw_scenes):
        if not isinstance(raw_scene, dict):
            raise ContentParseError(
                f"Field 'scenes[{index}]' must be an object."
            )

        scenes.append(
            ContentScene(
                scene_id=_require_string(
                    raw_scene,
                    "scene_id",
                    prefix=f"scenes[{index}].",
                ),
                narration=_require_string(
                    raw_scene,
                    "narration",
                    prefix=f"scenes[{index}].",
                ),
                visual_description=_require_string(
                    raw_scene,
                    "visual_description",
                    prefix=f"scenes[{index}].",
                ),
                duration_seconds=_require_number(
                    raw_scene,
                    "duration_seconds",
                    prefix=f"scenes[{index}].",
                ),
            )
        )

    lesson = Lesson(
        title=title,
        topic=topic,
        target_age=target_age,
        language=language,
        scenes=tuple(scenes),
    )

    validation_errors = validate_lesson(lesson)

    if validation_errors:
        details = "; ".join(
            f"{error.field}: {error.message}"
            for error in validation_errors
        )
        raise ContentParseError(f"Lesson validation failed: {details}")

    return lesson


def _require_string(
    data: dict[str, Any],
    field: str,
    *,
    prefix: str = "",
) -> str:
    """Read a required string field from a JSON object."""
    value = data.get(field)

    if not isinstance(value, str):
        raise ContentParseError(f"Field '{prefix}{field}' must be a string.")

    return value


def _require_integer(
    data: dict[str, Any],
    field: str,
) -> int:
    """Read a required integer field from a JSON object."""
    value = data.get(field)

    if isinstance(value, bool) or not isinstance(value, int):
        raise ContentParseError(f"Field '{field}' must be an integer.")

    return value


def _require_number(
    data: dict[str, Any],
    field: str,
    *,
    prefix: str = "",
) -> float:
    """Read a required numeric field from a JSON object."""
    value = data.get(field)

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContentParseError(f"Field '{prefix}{field}' must be a number.")

    numeric_value = float(value)

    if not math.isfinite(numeric_value):
        raise ContentParseError(
            f"Field '{prefix}{field}' must be a finite number."
        )

    return numeric_value         