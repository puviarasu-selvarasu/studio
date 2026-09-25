"""Tests for the lesson generation application service."""

from __future__ import annotations

import pytest

from kernel.application.lesson_generator import (
    LessonGenerationError,
    LessonGenerator,
)


class FakeLLM:
    """Provide deterministic LLM responses for unit tests."""

    def __init__(self, response: str) -> None:
        """Initialize the fake LLM."""
        self.response = response
        self.last_prompt: str | None = None
        self.last_system_prompt: str | None = None

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        """Return the configured response."""
        self.last_prompt = prompt
        self.last_system_prompt = system_prompt
        return self.response


VALID_LESSON_JSON = """
{
  "title": "Five Animal Words",
  "topic": "Animals",
  "target_age": 5,
  "language": "English",
  "scenes": [
    {
      "scene_id": "scene_1",
      "narration": "This is a cat.",
      "visual_description": "A friendly cat stands in a sunny park.",
      "duration_seconds": 5.0
    },
    {
      "scene_id": "scene_2",
      "narration": "This is a dog.",
      "visual_description": "A happy dog sits beside a tree.",
      "duration_seconds": 5.0
    }
  ]
}
"""


def test_generate_returns_validated_lesson() -> None:
    """Valid LLM JSON should become a Lesson."""
    fake_llm = FakeLLM(VALID_LESSON_JSON)
    generator = LessonGenerator(fake_llm)

    lesson = generator.generate(
        "Animals",
        target_age=5,
        language="English",
    )

    assert lesson.title == "Five Animal Words"
    assert lesson.topic == "Animals"
    assert lesson.target_age == 5
    assert len(lesson.scenes) == 2


def test_generate_sends_required_generation_context() -> None:
    """The generated prompt should contain the requested context."""
    fake_llm = FakeLLM(VALID_LESSON_JSON)
    generator = LessonGenerator(fake_llm)

    generator.generate(
        "Colours",
        target_age=6,
        language="English",
    )

    assert fake_llm.last_prompt is not None
    assert "Topic: Colours" in fake_llm.last_prompt
    assert "Target age: 6" in fake_llm.last_prompt
    assert "Language: English" in fake_llm.last_prompt
    assert fake_llm.last_system_prompt is not None
    assert "ONLY valid JSON" in fake_llm.last_system_prompt


def test_invalid_llm_json_becomes_generation_error() -> None:
    """Invalid LLM output should become a controlled application error."""
    fake_llm = FakeLLM("not valid json")
    generator = LessonGenerator(fake_llm)

    with pytest.raises(LessonGenerationError, match="invalid lesson JSON"):
        generator.generate(
            "Animals",
            target_age=5,
        )


def test_empty_topic_is_rejected_before_llm_call() -> None:
    """An empty topic should fail before calling the LLM."""
    fake_llm = FakeLLM(VALID_LESSON_JSON)
    generator = LessonGenerator(fake_llm)

    with pytest.raises(ValueError, match="topic"):
        generator.generate(
            "   ",
            target_age=5,
        )

    assert fake_llm.last_prompt is None


def test_invalid_target_age_is_rejected() -> None:
    """A non-positive target age should be rejected."""
    fake_llm = FakeLLM(VALID_LESSON_JSON)
    generator = LessonGenerator(fake_llm)

    with pytest.raises(ValueError, match="Target age"):
        generator.generate(
            "Animals",
            target_age=0,
        )


def test_empty_language_is_rejected() -> None:
    """An empty language should be rejected."""
    fake_llm = FakeLLM(VALID_LESSON_JSON)
    generator = LessonGenerator(fake_llm)

    with pytest.raises(ValueError, match="language"):
        generator.generate(
            "Animals",
            target_age=5,
            language="   ",
        )


def test_llm_failure_becomes_generation_error() -> None:
    """An LLM failure should become a controlled application error."""

    class FailingLLM:
        """Fake LLM that always fails."""

        def generate(
            self,
            prompt: str,
            *,
            system_prompt: str | None = None,
        ) -> str:
            """Raise a simulated provider failure."""
            raise RuntimeError("simulated LLM failure")

    generator = LessonGenerator(FailingLLM())

    with pytest.raises(LessonGenerationError, match="generation failed"):
        generator.generate(
            "Animals",
            target_age=5,
        )
