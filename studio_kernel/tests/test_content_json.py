"""Tests for the Studio content JSON boundary."""

from __future__ import annotations

import pytest
import json

from kernel.content import ContentParseError, lesson_from_json


VALID_LESSON_JSON = """
{
  "title": "Five Animal Words",
  "topic": "Animals",
  "target_age": 5,
  "language": "English",
  "scenes": [
    {
      "scene_id": "scene_01",
      "narration": "This is a cat.",
      "visual_description": "Momo points at a cat.",
      "duration_seconds": 6.0
    }
  ]
}
"""


def test_valid_json_becomes_lesson() -> None:
    """Valid JSON should produce a validated Lesson."""
    lesson = lesson_from_json(VALID_LESSON_JSON)

    assert lesson.title == "Five Animal Words"
    assert lesson.topic == "Animals"
    assert lesson.target_age == 5
    assert lesson.language == "English"
    assert len(lesson.scenes) == 1
    assert lesson.scenes[0].scene_id == "scene_01"
    assert lesson.scenes[0].duration_seconds == 6.0


def test_malformed_json_is_rejected() -> None:
    """Malformed JSON should never reach the domain model."""
    with pytest.raises(ContentParseError, match="Invalid JSON"):
        lesson_from_json("{invalid json")


def test_non_object_root_is_rejected() -> None:
    """The lesson JSON root must be an object."""
    with pytest.raises(ContentParseError, match="root must be an object"):
        lesson_from_json("[]")


def test_wrong_field_type_is_rejected() -> None:
    """Incorrect primitive types should be rejected."""
    json_text = VALID_LESSON_JSON.replace('"target_age": 5', '"target_age": "five"')

    with pytest.raises(ContentParseError, match="target_age.*integer"):
        lesson_from_json(json_text)


def test_missing_scene_field_is_rejected() -> None:
    """Missing required scene fields should be rejected."""
    json_text = VALID_LESSON_JSON.replace(
        '"visual_description": "Momo points at a cat.",\n',
        ""
    )

    with pytest.raises(ContentParseError, match="visual_description"):
        lesson_from_json(json_text)


def test_domain_validation_errors_are_rejected() -> None:
    """Structurally valid JSON with invalid domain values should fail."""
    json_text = VALID_LESSON_JSON.replace('"duration_seconds": 6.0', '"duration_seconds": 0')

    with pytest.raises(ContentParseError, match="duration_seconds"):
        lesson_from_json(json_text)
def test_boolean_target_age_is_rejected() -> None:
    """Boolean values must not be accepted as integer ages."""
    json_text = VALID_LESSON_JSON.replace(
        '"target_age": 5',
        '"target_age": true',
    )

    with pytest.raises(ContentParseError, match="target_age.*integer"):
        lesson_from_json(json_text)

def test_utf8_bom_is_accepted() -> None:
    """A UTF-8 BOM should not prevent valid JSON from being parsed."""
    json_text = "\ufeff" + VALID_LESSON_JSON

    lesson = lesson_from_json(json_text)

    assert lesson.title == json.loads(VALID_LESSON_JSON)["title"]

def test_non_finite_duration_is_rejected() -> None:
    """NaN durations must not enter the content domain."""
    data = json.loads(VALID_LESSON_JSON)
    data["scenes"][0]["duration_seconds"] = float("nan")

    json_text = json.dumps(data, allow_nan=True)

    with pytest.raises(ContentParseError, match="finite number"):
        lesson_from_json(json_text)