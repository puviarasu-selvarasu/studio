"""Domain models for Studio animation projects."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StudioProject:
    """Represent one isolated Studio animation production."""

    project_id: str
    title: str
    format: str
    genres: tuple[str, ...] = field(default_factory=tuple)