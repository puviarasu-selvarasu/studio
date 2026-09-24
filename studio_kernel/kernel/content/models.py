"""Domain models for Studio content."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ContentScene:
    """Represent one scene of generated content."""

    scene_id: str
    narration: str
    visual_description: str
    duration_seconds: float


@dataclass(frozen=True)
class Lesson:
    """Represent a complete educational lesson."""

    title: str
    topic: str
    target_age: int
    language: str
    scenes: tuple[ContentScene, ...] = field(default_factory=tuple)
