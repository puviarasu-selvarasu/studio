"""Tests for Studio's canonical humanoid rig contract."""

from __future__ import annotations

import pytest

from studio_kernel.kernel.adapters.blender.rig_contract import (
    HUMANOID_BONE_NAMES,
    HUMANOID_RIG,
    RigContractError,
    validate_rig_bones,
)


def test_humanoid_contract_contains_expected_bones() -> None:
    assert HUMANOID_BONE_NAMES == (
        "root",
        "pelvis",
        "spine",
        "chest",
        "neck",
        "head",
        "upper_arm.L",
        "forearm.L",
        "hand.L",
        "upper_arm.R",
        "forearm.R",
        "hand.R",
        "thigh.L",
        "shin.L",
        "foot.L",
        "thigh.R",
        "shin.R",
        "foot.R",
    )


def test_humanoid_contract_has_valid_parent_order() -> None:
    seen: set[str] = set()

    for bone in HUMANOID_RIG:
        if bone.parent is not None:
            assert bone.parent in seen

        seen.add(bone.name)


def test_exact_humanoid_contract_is_valid() -> None:
    validate_rig_bones(HUMANOID_BONE_NAMES)


def test_missing_bone_is_rejected() -> None:
    incomplete = tuple(
        name
        for name in HUMANOID_BONE_NAMES
        if name != "head"
    )

    with pytest.raises(
        RigContractError,
        match="missing required bone",
    ):
        validate_rig_bones(incomplete)


def test_unexpected_bone_is_rejected() -> None:
    expanded = HUMANOID_BONE_NAMES + (
        "unknown-control",
    )

    with pytest.raises(
        RigContractError,
        match="unexpected bone",
    ):
        validate_rig_bones(expanded)


def test_duplicate_bone_is_rejected() -> None:
    duplicated = HUMANOID_BONE_NAMES + (
        "head",
    )

    with pytest.raises(
        RigContractError,
        match="duplicate bone",
    ):
        validate_rig_bones(duplicated)
