"""Application service for generating validated lessons from an LLM."""

from __future__ import annotations

from kernel.content.json_codec import ContentParseError, lesson_from_json
from kernel.content.models import Lesson
from kernel.ports.llm import LLMPort


class LessonGenerationError(Exception):
    """Represent a failure while generating a valid lesson."""


class LessonGenerator:
    """Generate validated Lesson domain objects through an LLM port."""

    def __init__(self, llm: LLMPort) -> None:
        """Initialize the lesson generator.

        Args:
            llm: LLM implementation used to generate lesson content.
        """
        self._llm = llm

    def generate(
        self,
        topic: str,
        *,
        target_age: int,
        language: str = "English",
    ) -> Lesson:
        """Generate and validate a lesson for the requested topic.

        Args:
            topic: Educational topic for the lesson.
            target_age: Target learner age.
            language: Language of the lesson.

        Returns:
            A validated Lesson domain object.

        Raises:
            ValueError: If the input arguments are invalid.
            LessonGenerationError: If the LLM fails or returns invalid
                lesson JSON.
        """
        if not topic.strip():
            raise ValueError("Lesson topic must not be empty.")

        if target_age <= 0:
            raise ValueError("Target age must be greater than zero.")

        if not language.strip():
            raise ValueError("Lesson language must not be empty.")

        prompt = self._build_prompt(
            topic=topic,
            target_age=target_age,
            language=language,
        )

        try:
            raw_json = self._llm.generate(
                prompt,
                system_prompt=self._system_prompt(),
            )
        except Exception as exc:
            raise LessonGenerationError(
                f"Lesson generation failed: {exc}"
            ) from exc

        try:
            return lesson_from_json(raw_json)
        except ContentParseError as exc:
            raise LessonGenerationError(
                f"LLM returned invalid lesson JSON: {exc.message}"
            ) from exc

    @staticmethod
    def _system_prompt() -> str:
        """Return the system instruction for structured lesson generation."""
        return (
            "You are a lesson-generation component for the Studio animation "
            "platform. Return ONLY valid JSON. Do not use Markdown fences. "
            "Do not include explanations before or after the JSON."
        )

    @staticmethod
    def _build_prompt(
        *,
        topic: str,
        target_age: int,
        language: str,
    ) -> str:
        """Build the deterministic lesson-generation prompt."""
        return f"""
Create a short educational lesson for children.

Topic: {topic}
Target age: {target_age}
Language: {language}

Return ONLY a JSON object with exactly this structure:

{{
  "title": "string",
  "topic": "string",
  "target_age": {target_age},
  "language": "{language}",
  "scenes": [
    {{
      "scene_id": "scene_1",
      "narration": "string",
      "visual_description": "string",
      "duration_seconds": 5.0
    }}
  ]
}}

Requirements:
- Create 3 to 5 scenes.
- Every scene must contain narration.
- Every scene must contain a visual description.
- Every scene must have a positive duration.
- Keep the lesson suitable for the target age.
- Keep the content factually appropriate for the topic.
- Do not include Markdown.
- Do not include additional JSON fields.
""".strip()
