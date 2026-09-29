"""Domain models for character animation capabilities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CharacterCapability:
    """Describe the animation actions supported by one character."""

    character_id: str
    actions: tuple[str, ...] = field(default_factory=tuple)

    def supports(self, action: str) -> bool:
        """Return whether this character supports the requested action."""
        return action in self.actions


@dataclass(frozen=True)
class CapabilityRegistry:
    """Contain animation capabilities for all registered characters."""

    characters: tuple[CharacterCapability, ...] = field(default_factory=tuple)

    def get_character(self, character_id: str) -> CharacterCapability | None:
        """Return a character capability definition by ID."""
        for character in self.characters:
            if character.character_id == character_id:
                return character

        return None
