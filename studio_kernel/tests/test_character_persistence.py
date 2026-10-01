"""Tests for persistent Studio character identity and variants."""

from __future__ import annotations

import json

import pytest

from kernel.adapters.filesystem.character_catalog_store import (
    CharacterCatalogStoreError,
    load_character_catalog,
    save_character_catalog,
)
from kernel.characters import (
    CharacterCatalog,
    CharacterVariant,
    CharacterVariantAppearance,
    DEFAULT_CHARACTER_CATALOG,
    MOMO_DEFAULT_VARIANT,
    MOMO_IDENTITY,
)
from kernel.characters.serialization import (
    CHARACTER_CATALOG_SCHEMA_VERSION,
    CharacterCatalogSerializationError,
    character_catalog_from_json,
    character_catalog_to_json,
)


def _catalog_with_winter_variant() -> CharacterCatalog:
    winter = CharacterVariant(
        character_id="momo",
        variant_id="winter",
        display_name="Momo - Winter",
        appearance=CharacterVariantAppearance(
            summary="Momo wearing her winter appearance.",
            descriptors=(
                "winter coat",
                "winter scarf",
            ),
        ),
    )

    return CharacterCatalog(
        identities=(
            MOMO_IDENTITY,
        ),
        variants=(
            MOMO_DEFAULT_VARIANT,
            winter,
        ),
    )


def test_character_catalog_json_round_trip_preserves_domain_objects() -> None:
    raw_json = character_catalog_to_json(
        DEFAULT_CHARACTER_CATALOG
    )

    restored = character_catalog_from_json(
        raw_json
    )

    assert restored == DEFAULT_CHARACTER_CATALOG

    assert (
        restored.get_identity(
            "momo"
        )
        == MOMO_IDENTITY
    )

    assert (
        restored.get_variant(
            "momo",
            "default",
        )
        == MOMO_DEFAULT_VARIANT
    )


def test_character_catalog_json_is_deterministic() -> None:
    first = character_catalog_to_json(
        DEFAULT_CHARACTER_CATALOG
    )

    second = character_catalog_to_json(
        DEFAULT_CHARACTER_CATALOG
    )

    assert first == second

    data = json.loads(
        first
    )

    assert (
        data["schema_version"]
        == CHARACTER_CATALOG_SCHEMA_VERSION
        == 1
    )


def test_filesystem_store_persists_and_reloads_catalog(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "characters"
        / "catalog.json"
    )

    saved = save_character_catalog(
        DEFAULT_CHARACTER_CATALOG,
        path,
    )

    assert saved == path
    assert path.is_file()

    restored = load_character_catalog(
        path
    )

    assert restored == DEFAULT_CHARACTER_CATALOG


def test_separate_loads_preserve_identity_continuity(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "catalog.json"
    )

    save_character_catalog(
        DEFAULT_CHARACTER_CATALOG,
        path,
    )

    first_run = load_character_catalog(
        path
    )

    second_run = load_character_catalog(
        path
    )

    assert first_run == second_run
    assert first_run is not second_run

    first_identity = first_run.get_identity(
        "momo"
    )

    second_identity = second_run.get_identity(
        "momo"
    )

    assert first_identity is not None
    assert second_identity is not None

    assert (
        first_identity.character_id
        == second_identity.character_id
        == "momo"
    )

    assert first_identity == second_identity


def test_variant_identity_survives_persistence(
    tmp_path,
) -> None:
    catalog = _catalog_with_winter_variant()

    path = (
        tmp_path
        / "catalog.json"
    )

    save_character_catalog(
        catalog,
        path,
    )

    restored = load_character_catalog(
        path
    )

    winter = restored.get_variant(
        "momo",
        "winter",
    )

    assert winter is not None
    assert winter.character_id == "momo"
    assert winter.variant_id == "winter"

    assert winter.appearance.descriptors == (
        "winter coat",
        "winter scarf",
    )


def test_serialization_rejects_unknown_schema_version() -> None:
    data = json.loads(
        character_catalog_to_json(
            DEFAULT_CHARACTER_CATALOG
        )
    )

    data["schema_version"] = 999

    with pytest.raises(
        CharacterCatalogSerializationError,
        match="Unsupported.*schema version",
    ):
        character_catalog_from_json(
            json.dumps(
                data
            )
        )


def test_serialization_rejects_unexpected_fields() -> None:
    data = json.loads(
        character_catalog_to_json(
            DEFAULT_CHARACTER_CATALOG
        )
    )

    data["unsafe_extra"] = (
        "must not be accepted"
    )

    with pytest.raises(
        CharacterCatalogSerializationError,
        match="invalid fields",
    ):
        character_catalog_from_json(
            json.dumps(
                data
            )
        )


def test_filesystem_store_rejects_invalid_persisted_catalog(
    tmp_path,
) -> None:
    path = (
        tmp_path
        / "catalog.json"
    )

    path.write_text(
        '{"schema_version": 999, "identities": [], "variants": []}\n',
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(
        CharacterCatalogStoreError,
        match="Unable to load",
    ):
        load_character_catalog(
            path
        )
