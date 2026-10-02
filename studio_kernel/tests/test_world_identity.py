"""Tests for pure Studio world, location, and prop identity contracts."""

from __future__ import annotations

from dataclasses import (
    FrozenInstanceError,
    fields,
)
from pathlib import Path

import pytest

from kernel.worlds import (
    LocationIdentity,
    LocationVariant,
    PropIdentity,
    PropVariant,
    WorldIdentity,
    WorldIdentityError,
)


MODELS_SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "worlds"
    / "models.py"
)


def test_world_identity_preserves_persistent_setting_anchors() -> None:
    world = WorldIdentity(
        world_id="studio_world",
        display_name="Studio World",
        summary="The persistent narrative setting.",
        anchors=(
            "grounded contemporary architecture",
            "restrained technology",
            "consistent regional visual language",
        ),
    )

    assert world.world_id == "studio_world"

    assert world.anchors == (
        "grounded contemporary architecture",
        "restrained technology",
        "consistent regional visual language",
    )


def test_location_identity_belongs_to_world_without_embedding_variant() -> None:
    location = LocationIdentity(
        world_id="studio_world",
        location_id="old_station",
        display_name="Old Railway Station",
        summary="A persistent railway station location.",
        anchors=(
            "long central platform",
            "aged station canopy",
            "recognizable platform sign",
        ),
    )

    assert location.world_id == "studio_world"
    assert location.location_id == "old_station"


def test_location_variant_keeps_context_separate_from_location_identity() -> None:
    variant = LocationVariant(
        world_id="studio_world",
        location_id="old_station",
        variant_id="rainy_night",
        display_name="Old Railway Station - Rainy Night",
        summary="The station during a restrained rainy night.",
        descriptors=(
            "wet platform surfaces",
            "cool night atmosphere",
            "warm practical light accents",
        ),
    )

    assert variant.location_id == "old_station"
    assert variant.variant_id == "rainy_night"


def test_prop_identity_is_world_scoped_and_persistent() -> None:
    prop = PropIdentity(
        world_id="studio_world",
        prop_id="momo_phone",
        display_name="Momo's Phone",
        summary="Momo's persistent personal phone.",
        anchors=(
            "compact rectangular silhouette",
            "dark casing",
            "small accent detail",
        ),
    )

    assert prop.world_id == "studio_world"
    assert prop.prop_id == "momo_phone"


def test_prop_variant_does_not_create_a_new_prop_identity() -> None:
    variant = PropVariant(
        world_id="studio_world",
        prop_id="momo_phone",
        variant_id="screen_on",
        display_name="Momo's Phone - Screen On",
        summary="The same phone with its display active.",
        descriptors=(
            "illuminated screen",
            "identity silhouette unchanged",
        ),
    )

    assert variant.prop_id == "momo_phone"
    assert variant.variant_id == "screen_on"


def test_world_contracts_are_immutable() -> None:
    world = WorldIdentity(
        world_id="studio_world",
        display_name="Studio World",
        summary="Persistent narrative setting.",
        anchors=(
            "stable visual geography",
        ),
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        world.world_id = "changed"


@pytest.mark.parametrize(
    "invalid_id",
    (
        "",
        "Has Space",
        "Upper",
        "1starts_with_digit",
        "bad!",
    ),
)
def test_world_identity_rejects_invalid_stable_identifiers(
    invalid_id: str,
) -> None:
    with pytest.raises(
        WorldIdentityError,
        match="stable lowercase identifier",
    ):
        WorldIdentity(
            world_id=invalid_id,
            display_name="World",
            summary="Summary",
            anchors=(
                "anchor",
            ),
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "display_name",
        "summary",
    ),
)
def test_world_identity_rejects_empty_required_text(
    field_name: str,
) -> None:
    values = {
        "world_id": "studio_world",
        "display_name": "Studio World",
        "summary": "Summary",
        "anchors": (
            "anchor",
        ),
    }

    values[field_name] = "   "

    with pytest.raises(
        WorldIdentityError,
        match="must not be empty",
    ):
        WorldIdentity(
            **values
        )


def test_identity_anchors_must_be_unique() -> None:
    with pytest.raises(
        WorldIdentityError,
        match="unique",
    ):
        LocationIdentity(
            world_id="studio_world",
            location_id="old_station",
            display_name="Old Railway Station",
            summary="Persistent station.",
            anchors=(
                "platform sign",
                "platform sign",
            ),
        )


def test_variant_descriptors_must_be_unique() -> None:
    with pytest.raises(
        WorldIdentityError,
        match="unique",
    ):
        PropVariant(
            world_id="studio_world",
            prop_id="momo_phone",
            variant_id="screen_on",
            display_name="Phone - Screen On",
            summary="Active phone screen.",
            descriptors=(
                "illuminated screen",
                "illuminated screen",
            ),
        )


def test_identity_contracts_keep_variants_and_production_data_separate() -> None:
    world_fields = {
        item.name
        for item in fields(
            WorldIdentity
        )
    }

    location_fields = {
        item.name
        for item in fields(
            LocationIdentity
        )
    }

    prop_fields = {
        item.name
        for item in fields(
            PropIdentity
        )
    }

    assert "variant_id" not in world_fields
    assert "variant_id" not in location_fields
    assert "variant_id" not in prop_fields

    forbidden_production_fields = {
        "mesh_path",
        "blend_path",
        "texture_path",
        "object_name",
        "location",
        "rotation",
        "scale",
        "coordinates",
        "python_code",
    }

    assert world_fields.isdisjoint(
        forbidden_production_fields
    )

    assert location_fields.isdisjoint(
        forbidden_production_fields
    )

    assert prop_fields.isdisjoint(
        forbidden_production_fields
    )


def test_world_models_are_pure_domain_data() -> None:
    source = MODELS_SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "import bpy",
        "from bpy",
        "pydantic",
        "kernel.adapters",
        "pathlib",
        "subprocess",
        "json.",
        "eval(",
        "exec(",
    )

    for token in forbidden:
        assert token not in source
