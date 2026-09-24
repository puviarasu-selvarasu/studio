"""Tests for Studio content domain models and validation."""

from __future__ import annotations

from kernel.content import ContentScene, Lesson, validate_lesson


def test_valid_lesson_has_no_errors() -> None:
    """A structurally valid lesson should pass validation."""
    lesson = Lesson(
        title="Five Animal Words",
        topic="Animals",
        target_age=5,
        language="English",
        scenes=(
            ContentScene(
                scene_id="scene_01",
                narration="This is a cat.",
                visual_description="Momo points at a cat.",
                duration_seconds=6.0,
            ),
        ),
    )

    assert validate_lesson(lesson) == []


def test_empty_lesson_is_invalid() -> None:
    """Required lesson fields must not be empty."""
    lesson = Lesson(
        title="",
        topic="",
        target_age=0,
        language="",
    )

    errors = validate_lesson(lesson)

    fields = {error.field for error in errors}

    assert "title" in fields
    assert "topic" in fields
    assert "target_age" in fields
    assert "language" in fields
    assert "scenes" in fields


def test_invalid_scene_is_detected() -> None:
    """Invalid scene fields should be reported."""
    lesson = Lesson(
        title="Animals",
        topic="Animals",
        target_age=5,
        language="English",
        scenes=(
            ContentScene(
                scene_id="",
                narration="",
                visual_description="",
                duration_seconds=0.0,
            ),
        ),
    )

    errors = validate_lesson(lesson)

    fields = {error.field for error in errors}

    assert "scenes[0].scene_id" in fields
    assert "scenes[0].narration" in fields
    assert "scenes[0].visual_description" in fields
    assert "scenes[0].duration_seconds" in fields
