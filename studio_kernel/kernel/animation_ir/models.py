"""Domain models for Studio Animation IR."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnimationAction:
    """Describe one deterministic character action."""

    action: str
    start_seconds: float
    duration_seconds: float


@dataclass(frozen=True)
class CharacterAnimation:
    """Describe animation assigned to one character."""

    character_id: str
    actions: tuple[AnimationAction, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AnimationScene:
    """Describe the complete animation intent for one scene."""

    scene_id: str
    duration_seconds: float
    characters: tuple[CharacterAnimation, ...] = field(default_factory=tuple)
