"""Tests for Studio persistent character identity contracts."""

from __future__ import annotations

from dataclasses import (
    FrozenInstanceError,
    fields,
)
from pathlib import Path

import pytest

from kernel.characters import (
    CharacterAppearanceIdentity,
    CharacterIdentity,
    CharacterIdentityError,
    CharacterPerformanceIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
)


MODELS = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "characters"
    / "models.py"
)


def _identity() -> CharacterIdentity:
    return CharacterIdentity(
        character_id="momo",
        display_name="Momo",
        appearance=CharacterAppearanceIdentity(
            summary=(
                "A recognizable young anime character with "
                "a clean readable silhouette."
            ),
            anchors=(
                "recognizable silhouette",
                "consistent facial proportions",
                "stable core color identity",
            ),
        ),
        performance=CharacterPerformanceIdentity(
            summary=(
                "Expressive but restrained acting with "
                "clear readable poses."
            ),
            traits=(
                "observant",
                "warm",
                "deliberate movement",
            ),
        ),
    )


def test_character_identity_preserves_stable_metadata() -> None:
    identity = _identity()

    assert identity.character_id == "momo"
    assert identity.display_name == "Momo"

    assert (
        identity.appearance.anchors[0]
        == "recognizable silhouette"
    )

    assert (
        identity.performance.traits
        == (
            "observant",
            "warm",
            "deliberate movement",
        )
    )


def test_character_identity_contract_is_immutable() -> None:
    identity = _identity()

    with pytest.raises(
        FrozenInstanceError
    ):
        identity.display_name = "Changed"


@pytest.mark.parametrize(
    "character_id",
    (
        "",
        "   ",
        "Momo",
        "momo hero",
        "_momo",
    ),
)
def test_character_identity_rejects_invalid_stable_id(
    character_id: str,
) -> None:
    with pytest.raises(
        CharacterIdentityError,
        match="character_id",
    ):
        CharacterIdentity(
            character_id=character_id,
            display_name="Momo",
            appearance=CharacterAppearanceIdentity(
                summary="Stable appearance.",
                anchors=(
                    "stable silhouette",
                ),
            ),
            performance=CharacterPerformanceIdentity(
                summary="Stable performance.",
                traits=(
                    "deliberate",
                ),
            ),
        )


def test_appearance_identity_requires_unique_anchors() -> None:
    with pytest.raises(
        CharacterIdentityError,
        match="duplicates",
    ):
        CharacterAppearanceIdentity(
            summary="Stable appearance.",
            anchors=(
                "dark hair",
                "dark hair",
            ),
        )


def test_performance_identity_requires_unique_traits() -> None:
    with pytest.raises(
        CharacterIdentityError,
        match="duplicates",
    ):
        CharacterPerformanceIdentity(
            summary="Stable performance.",
            traits=(
                "reserved",
                "reserved",
            ),
        )


def test_character_identity_requires_domain_subcontracts() -> None:
    appearance = CharacterAppearanceIdentity(
        summary="Stable appearance.",
        anchors=(
            "clear silhouette",
        ),
    )

    performance = CharacterPerformanceIdentity(
        summary="Stable performance.",
        traits=(
            "controlled",
        ),
    )

    with pytest.raises(
        CharacterIdentityError,
        match="appearance",
    ):
        CharacterIdentity(
            character_id="momo",
            display_name="Momo",
            appearance="not-an-appearance",
            performance=performance,
        )

    with pytest.raises(
        CharacterIdentityError,
        match="performance",
    ):
        CharacterIdentity(
            character_id="momo",
            display_name="Momo",
            appearance=appearance,
            performance="not-a-performance",
        )


def test_identity_contract_does_not_mix_variant_or_blender_assets() -> None:
    names = {
        field.name
        for field in fields(
            CharacterIdentity
        )
    }

    assert names == {
        "character_id",
        "display_name",
        "appearance",
        "performance",
    }

    assert "variant_id" not in names

    source = MODELS.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "bpy",
        "Blender",
        "Ollama",
        "Pydantic",
        "mesh_path",
        "rig_path",
        "outfit_id",
    )

    for token in forbidden:
        assert token not in source

def _variant() -> CharacterVariant:
    return CharacterVariant(
        character_id="momo",
        variant_id="default",
        display_name="Momo - Default",
        appearance=CharacterVariantAppearance(
            summary=(
                "Momo's default everyday appearance."
            ),
            descriptors=(
                "shoulder-length dark hair",
                "simple everyday outfit",
                "clean readable silhouette",
            ),
        ),
    )


def test_character_variant_references_identity_without_redefining_it() -> None:
    variant = _variant()

    assert variant.character_id == "momo"
    assert variant.variant_id == "default"
    assert variant.display_name == "Momo - Default"

    assert (
        variant.appearance.descriptors
        == (
            "shoulder-length dark hair",
            "simple everyday outfit",
            "clean readable silhouette",
        )
    )


def test_character_variant_contract_is_immutable() -> None:
    variant = _variant()

    with pytest.raises(
        FrozenInstanceError
    ):
        variant.variant_id = "winter"


@pytest.mark.parametrize(
    "variant_id",
    (
        "",
        "   ",
        "Default",
        "school uniform",
        "_default",
    ),
)
def test_character_variant_rejects_invalid_variant_id(
    variant_id: str,
) -> None:
    with pytest.raises(
        CharacterIdentityError,
        match="variant_id",
    ):
        CharacterVariant(
            character_id="momo",
            variant_id=variant_id,
            display_name="Variant",
            appearance=CharacterVariantAppearance(
                summary="Variant appearance.",
                descriptors=(
                    "different outfit",
                ),
            ),
        )


def test_variant_rejects_invalid_character_reference() -> None:
    with pytest.raises(
        CharacterIdentityError,
        match="character_id",
    ):
        CharacterVariant(
            character_id="Momo",
            variant_id="default",
            display_name="Default",
            appearance=CharacterVariantAppearance(
                summary="Variant appearance.",
                descriptors=(
                    "different outfit",
                ),
            ),
        )


def test_variant_appearance_requires_unique_descriptors() -> None:
    with pytest.raises(
        CharacterIdentityError,
        match="duplicates",
    ):
        CharacterVariantAppearance(
            summary="Variant appearance.",
            descriptors=(
                "winter coat",
                "winter coat",
            ),
        )


def test_variant_does_not_redefine_character_performance_identity() -> None:
    names = {
        field.name
        for field in fields(
            CharacterVariant
        )
    }

    assert names == {
        "character_id",
        "variant_id",
        "display_name",
        "appearance",
    }

    assert "performance" not in names


def test_variant_contract_does_not_contain_production_assets() -> None:
    source = MODELS.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "import bpy",
        "from bpy",
        "mesh_path",
        "rig_path",
        "blend_path",
        "texture_path",
        "material_path",
        "armature_path",
    )

    for token in forbidden:
        assert token not in source


def test_identity_and_variant_are_distinct_domain_concepts() -> None:
    identity = _identity()
    variant = _variant()

    assert identity.character_id == variant.character_id

    assert not hasattr(
        identity,
        "variant_id",
    )

    assert not hasattr(
        variant,
        "performance",
    )

    assert (
        identity.appearance
        != variant.appearance
    )
