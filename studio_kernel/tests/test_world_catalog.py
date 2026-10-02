"""Tests for Studio's pure world catalog and canonical first location."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.worlds import (
    DEFAULT_WORLD_CATALOG,
    OLD_STATION,
    OLD_STATION_DEFAULT,
    OLD_STATION_RAINY_NIGHT,
    STATION_BENCH,
    STATION_BENCH_DEFAULT,
    STUDIO_WORLD,
    LocationIdentity,
    LocationVariant,
    PropIdentity,
    PropVariant,
    WorldCatalog,
    WorldCatalogError,
    WorldIdentity,
)


CATALOG_SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "worlds"
    / "catalog.py"
)


def test_default_catalog_resolves_canonical_world_and_station() -> None:
    assert (
        DEFAULT_WORLD_CATALOG.get_world(
            "studio_world"
        )
        == STUDIO_WORLD
    )

    assert (
        DEFAULT_WORLD_CATALOG.get_location(
            "studio_world",
            "old_station",
        )
        == OLD_STATION
    )


def test_default_location_variant_is_canonical_station_presentation() -> None:
    assert (
        DEFAULT_WORLD_CATALOG.get_location_variant(
            "studio_world",
            "old_station",
        )
        == OLD_STATION_DEFAULT
    )


def test_rainy_night_is_same_location_identity_with_new_context() -> None:
    rainy = (
        DEFAULT_WORLD_CATALOG.get_location_variant(
            "studio_world",
            "old_station",
            "rainy_night",
        )
    )

    assert rainy == OLD_STATION_RAINY_NIGHT
    assert rainy.location_id == OLD_STATION.location_id
    assert rainy.world_id == OLD_STATION.world_id


def test_default_catalog_resolves_canonical_station_prop() -> None:
    assert (
        DEFAULT_WORLD_CATALOG.get_prop(
            "studio_world",
            "station_bench",
        )
        == STATION_BENCH
    )

    assert (
        DEFAULT_WORLD_CATALOG.get_prop_variant(
            "studio_world",
            "station_bench",
        )
        == STATION_BENCH_DEFAULT
    )


def test_catalog_filters_locations_and_props_by_world() -> None:
    assert (
        DEFAULT_WORLD_CATALOG.locations_for(
            "studio_world"
        )
        == (
            OLD_STATION,
        )
    )

    assert (
        DEFAULT_WORLD_CATALOG.props_for(
            "studio_world"
        )
        == (
            STATION_BENCH,
        )
    )


def test_catalog_missing_lookups_return_none() -> None:
    assert (
        DEFAULT_WORLD_CATALOG.get_world(
            "missing"
        )
        is None
    )

    assert (
        DEFAULT_WORLD_CATALOG.get_location(
            "studio_world",
            "missing",
        )
        is None
    )

    assert (
        DEFAULT_WORLD_CATALOG.get_prop(
            "studio_world",
            "missing",
        )
        is None
    )


def test_catalog_rejects_duplicate_world_identity() -> None:
    with pytest.raises(
        WorldCatalogError,
        match="Duplicate world_id",
    ):
        WorldCatalog(
            worlds=(
                STUDIO_WORLD,
                STUDIO_WORLD,
            ),
        )


def test_catalog_rejects_duplicate_location_identity() -> None:
    with pytest.raises(
        WorldCatalogError,
        match="Duplicate location identity",
    ):
        WorldCatalog(
            worlds=(
                STUDIO_WORLD,
            ),
            locations=(
                OLD_STATION,
                OLD_STATION,
            ),
        )


def test_catalog_rejects_orphan_location() -> None:
    orphan = LocationIdentity(
        world_id="missing_world",
        location_id="orphan",
        display_name="Orphan Location",
        summary="Invalid orphan.",
        anchors=(
            "orphan anchor",
        ),
    )

    with pytest.raises(
        WorldCatalogError,
        match="unknown world",
    ):
        WorldCatalog(
            worlds=(
                STUDIO_WORLD,
            ),
            locations=(
                orphan,
            ),
        )


def test_catalog_rejects_orphan_location_variant() -> None:
    orphan = LocationVariant(
        world_id="studio_world",
        location_id="missing",
        variant_id="default",
        display_name="Missing Location Variant",
        summary="Invalid orphan variant.",
        descriptors=(
            "orphan descriptor",
        ),
    )

    with pytest.raises(
        WorldCatalogError,
        match="unknown location",
    ):
        WorldCatalog(
            worlds=(
                STUDIO_WORLD,
            ),
            location_variants=(
                orphan,
            ),
        )


def test_catalog_rejects_orphan_prop() -> None:
    orphan = PropIdentity(
        world_id="missing_world",
        prop_id="orphan_prop",
        display_name="Orphan Prop",
        summary="Invalid orphan prop.",
        anchors=(
            "orphan anchor",
        ),
    )

    with pytest.raises(
        WorldCatalogError,
        match="unknown world",
    ):
        WorldCatalog(
            worlds=(
                STUDIO_WORLD,
            ),
            props=(
                orphan,
            ),
        )


def test_catalog_rejects_orphan_prop_variant() -> None:
    orphan = PropVariant(
        world_id="studio_world",
        prop_id="missing",
        variant_id="default",
        display_name="Missing Prop Variant",
        summary="Invalid orphan variant.",
        descriptors=(
            "orphan descriptor",
        ),
    )

    with pytest.raises(
        WorldCatalogError,
        match="unknown prop",
    ):
        WorldCatalog(
            worlds=(
                STUDIO_WORLD,
            ),
            prop_variants=(
                orphan,
            ),
        )


def test_world_catalog_remains_pure_domain_data() -> None:
    source = CATALOG_SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "import bpy",
        "from bpy",
        "kernel.adapters",
        "kernel.application",
        "pathlib",
        "subprocess",
        "json.",
        "eval(",
        "exec(",
        "mesh_path",
        "blend_path",
        "texture_path",
        "coordinates",
    )

    for token in forbidden:
        assert token not in source
