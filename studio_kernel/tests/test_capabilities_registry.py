"""Tests for the Studio character capability registry."""

from __future__ import annotations

import json
from pathlib import Path


REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "kernel"
    / "assets"
    / "capabilities.json"
)


def test_capability_registry_exists() -> None:
    """The capability registry must exist in the kernel assets."""
    assert REGISTRY_PATH.is_file()


def test_capability_registry_is_valid_json() -> None:
    """The capability registry must contain valid JSON."""
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    assert isinstance(data, dict)


def test_momo_capability_contract() -> None:
    """Momo must expose the initial Studio action capabilities."""
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    assert "characters" in data
    assert "momo" in data["characters"]

    momo = data["characters"]["momo"]

    assert isinstance(momo, dict)
    assert momo["actions"] == [
        "idle",
        "turn_head",
        "wave",
        "step_forward",
    ]


def test_capability_actions_are_unique_strings() -> None:
    """Capability actions must be unique non-empty strings."""
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    for character in data["characters"].values():
        actions = character["actions"]

        assert isinstance(actions, list)
        assert len(actions) == len(set(actions))

        for action in actions:
            assert isinstance(action, str)
            assert action.strip()
