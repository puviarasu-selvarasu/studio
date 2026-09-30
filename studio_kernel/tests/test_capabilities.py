"""Tests for the capability domain model and loader."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kernel.capabilities import (
    CapabilityLoadError,
    CapabilityRegistry,
    CharacterCapability,
    load_capability_registry,
)


REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "kernel"
    / "assets"
    / "capabilities.json"
)


def test_character_capability_supports_action() -> None:
    """A character should report supported actions correctly."""
    capability = CharacterCapability(
        character_id="momo",
        actions=("idle", "wave"),
    )

    assert capability.supports("wave")
    assert not capability.supports("jump")


def test_registry_returns_character() -> None:
    """The registry should locate a character by ID."""
    momo = CharacterCapability(
        character_id="momo",
        actions=("idle", "wave"),
    )
    registry = CapabilityRegistry(characters=(momo,))

    assert registry.get_character("momo") == momo


def test_registry_returns_none_for_unknown_character() -> None:
    """Unknown character IDs should return None."""
    registry = CapabilityRegistry()

    assert registry.get_character("unknown") is None


def test_load_real_capability_registry() -> None:
    """The real Studio capability registry should load successfully."""
    registry = load_capability_registry(REGISTRY_PATH)

    momo = registry.get_character("momo")

    assert momo is not None
    assert momo.actions == (
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    )


def test_loader_rejects_missing_characters(tmp_path: Path) -> None:
    """The loader should reject a registry without characters."""
    path = tmp_path / "capabilities.json"
    path.write_text("{}", encoding="utf-8")

    with pytest.raises(CapabilityLoadError):
        load_capability_registry(path)


def test_loader_rejects_non_list_actions(tmp_path: Path) -> None:
    """The loader should reject actions that are not lists."""
    path = tmp_path / "capabilities.json"
    path.write_text(
        json.dumps(
            {
                "characters": {
                    "momo": {
                        "actions": "wave",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CapabilityLoadError):
        load_capability_registry(path)


def test_loader_rejects_duplicate_actions(tmp_path: Path) -> None:
    """The loader should reject duplicate actions."""
    path = tmp_path / "capabilities.json"
    path.write_text(
        json.dumps(
            {
                "characters": {
                    "momo": {
                        "actions": ["idle", "idle"],
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CapabilityLoadError):
        load_capability_registry(path)
