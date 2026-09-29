"""Load character capabilities from the Studio capability registry."""

from __future__ import annotations

import json
from pathlib import Path

from .models import CapabilityRegistry, CharacterCapability


class CapabilityLoadError(Exception):
    """Represent a failure while loading the capability registry."""


def load_capability_registry(path: Path) -> CapabilityRegistry:
    """Load and validate a capability registry from a JSON file."""

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CapabilityLoadError(
            f"Unable to read capability registry: {path}"
        ) from exc

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise CapabilityLoadError(
            f"Capability registry contains invalid JSON: {path}"
        ) from exc

    if not isinstance(data, dict):
        raise CapabilityLoadError(
            "Capability registry root must be a JSON object."
        )

    characters_data = data.get("characters")

    if not isinstance(characters_data, dict):
        raise CapabilityLoadError(
            "Capability registry must contain a 'characters' object."
        )

    characters: list[CharacterCapability] = []

    for character_id, character_data in characters_data.items():
        if not isinstance(character_id, str) or not character_id.strip():
            raise CapabilityLoadError(
                "Character IDs must be non-empty strings."
            )

        if not isinstance(character_data, dict):
            raise CapabilityLoadError(
                f"Character '{character_id}' must be a JSON object."
            )

        actions = character_data.get("actions")

        if not isinstance(actions, list):
            raise CapabilityLoadError(
                f"Character '{character_id}' must define an 'actions' list."
            )

        if not all(isinstance(action, str) for action in actions):
            raise CapabilityLoadError(
                f"Character '{character_id}' actions must all be strings."
            )

        normalized_actions = tuple(action.strip() for action in actions)

        if any(not action for action in normalized_actions):
            raise CapabilityLoadError(
                f"Character '{character_id}' contains an empty action."
            )

        if len(normalized_actions) != len(set(normalized_actions)):
            raise CapabilityLoadError(
                f"Character '{character_id}' contains duplicate actions."
            )

        characters.append(
            CharacterCapability(
                character_id=character_id,
                actions=normalized_actions,
            )
        )

    return CapabilityRegistry(characters=tuple(characters))
