"""Tests for Studio's canonical character catalog."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.characters import (
    CharacterAppearanceIdentity,
    CharacterCatalog,
    CharacterCatalogError,
    CharacterIdentity,
    CharacterPerformanceIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
    DEFAULT_CHARACTER_CATALOG,
    MOMO_DEFAULT_VARIANT,
    MOMO_IDENTITY,
)


CATALOG_SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "characters"
    / "catalog.py"
)


def _identity(
    character_id: str,
    display_name: str,
) -> CharacterIdentity:
    return CharacterIdentity(
        character_id=character_id,
        display_name=display_name,
        appearance=CharacterAppearanceIdentity(
            summary="Stable appearance.",
            anchors=(
                "recognizable silhouette",
            ),
        ),
        performance=CharacterPerformanceIdentity(
            summary="Stable performance.",
            traits=(
                "deliberate",
            ),
        ),
    )


def _variant(
    character_id: str,
    variant_id: str,
) -> CharacterVariant:
    return CharacterVariant(
        character_id=character_id,
        variant_id=variant_id,
        display_name=(
            character_id
            + " - "
            + variant_id
        ),
        appearance=CharacterVariantAppearance(
            summary="Variant appearance.",
            descriptors=(
                "variant-specific appearance",
            ),
        ),
    )


def test_default_catalog_contains_momo_identity() -> None:
    identity = DEFAULT_CHARACTER_CATALOG.get_identity(
        "momo"
    )

    assert identity is MOMO_IDENTITY
    assert identity.display_name == "Momo"

    assert identity.appearance.anchors == (
        "recognizable silhouette",
        "consistent facial proportions",
        "stable core color identity",
    )

    assert identity.performance.traits == (
        "observant",
        "warm",
        "deliberate movement",
    )


def test_default_catalog_contains_momo_default_variant() -> None:
    variant = DEFAULT_CHARACTER_CATALOG.get_variant(
        "momo"
    )

    assert variant is MOMO_DEFAULT_VARIANT
    assert variant.character_id == "momo"
    assert variant.variant_id == "default"

    assert variant.appearance.descriptors == (
        "default hairstyle",
        "default everyday outfit",
        "default palette relationship",
    )


def test_catalog_unknown_identity_returns_none() -> None:
    assert (
        DEFAULT_CHARACTER_CATALOG.get_identity(
            "unknown"
        )
        is None
    )


def test_catalog_unknown_variant_returns_none() -> None:
    assert (
        DEFAULT_CHARACTER_CATALOG.get_variant(
            "momo",
            "unknown",
        )
        is None
    )


def test_catalog_returns_variants_for_identity() -> None:
    variants = (
        DEFAULT_CHARACTER_CATALOG.variants_for(
            "momo"
        )
    )

    assert variants == (
        MOMO_DEFAULT_VARIANT,
    )


def test_catalog_rejects_duplicate_character_ids() -> None:
    identity = _identity(
        "akira",
        "Akira",
    )

    duplicate = _identity(
        "akira",
        "Another Akira",
    )

    with pytest.raises(
        CharacterCatalogError,
        match="duplicate character",
    ):
        CharacterCatalog(
            identities=(
                identity,
                duplicate,
            ),
        )


def test_catalog_rejects_duplicate_variant_keys() -> None:
    identity = _identity(
        "akira",
        "Akira",
    )

    variant = _variant(
        "akira",
        "default",
    )

    duplicate = _variant(
        "akira",
        "default",
    )

    with pytest.raises(
        CharacterCatalogError,
        match="duplicate character variants",
    ):
        CharacterCatalog(
            identities=(
                identity,
            ),
            variants=(
                variant,
                duplicate,
            ),
        )


def test_catalog_rejects_orphan_variant() -> None:
    with pytest.raises(
        CharacterCatalogError,
        match="unknown character",
    ):
        CharacterCatalog(
            variants=(
                _variant(
                    "akira",
                    "default",
                ),
            ),
        )


def test_catalog_rejects_non_identity_member() -> None:
    with pytest.raises(
        CharacterCatalogError,
        match="CharacterIdentity",
    ):
        CharacterCatalog(
            identities=(
                "not-an-identity",
            ),
        )


def test_catalog_rejects_non_variant_member() -> None:
    identity = _identity(
        "akira",
        "Akira",
    )

    with pytest.raises(
        CharacterCatalogError,
        match="CharacterVariant",
    ):
        CharacterCatalog(
            identities=(
                identity,
            ),
            variants=(
                "not-a-variant",
            ),
        )


def test_catalog_remains_independent_of_production_assets_and_ai() -> None:
    source = CATALOG_SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "bpy",
        "Blender",
        "Ollama",
        "Pydantic",
        "CapabilityRegistry",
        "mesh_path",
        "rig_path",
        "blend_path",
        "texture_path",
        "armature",
    )

    for token in forbidden:
        assert token not in source
