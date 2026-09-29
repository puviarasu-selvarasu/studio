"""Validate Animation IR actions against character capabilities."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.animation_ir.models import AnimationScene
from .models import CapabilityRegistry


@dataclass(frozen=True)
class CapabilityValidationError(Exception):
    """Represent an unsupported animation capability request."""

    character_id: str
    action: str
    message: str

    def __str__(self) -> str:
        """Return a human-readable validation message."""
        return self.message


def validate_animation_capabilities(
    scene: AnimationScene,
    registry: CapabilityRegistry,
) -> None:
    """Validate every requested animation action against the registry."""

    for character in scene.characters:
        capability = registry.get_character(character.character_id)

        if capability is None:
            raise CapabilityValidationError(
                character_id=character.character_id,
                action="",
                message=(
                    f"Character '{character.character_id}' is not "
                    "registered in the capability registry."
                ),
            )

        for animation_action in character.actions:
            if not capability.supports(animation_action.action):
                raise CapabilityValidationError(
                    character_id=character.character_id,
                    action=animation_action.action,
                    message=(
                        f"Character '{character.character_id}' does not "
                        f"support animation action "
                        f"'{animation_action.action}'."
                    ),
                )
