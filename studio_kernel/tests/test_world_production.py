"""Tests for bounded deterministic Studio world production."""

from __future__ import annotations

from dataclasses import (
    FrozenInstanceError,
    fields,
)
from pathlib import Path

import pytest

from kernel.worlds import (
    OLD_STATION,
    OLD_STATION_DEFAULT,
    OLD_STATION_RAINY_NIGHT,
    STATION_BENCH,
    STATION_BENCH_DEFAULT,
    STUDIO_WORLD,
    ArchitectureProfile,
    AtmosphereStateProfile,
    EnvironmentDepthProfile,
    LocationIdentity,
    LocationLayoutProfile,
    LocationVariant,
    PropGeometryProfile,
    PropIdentity,
    PropProductionSpec,
    PropVariant,
    SurfaceStateProfile,
    WorldIdentity,
    WorldProductionSpec,
    WorldProductionSpecError,
    compile_world_production,
)


SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "worlds"
    / "production.py"
)


def compile_default(
) -> WorldProductionSpec:
    return compile_world_production(
        STUDIO_WORLD,
        OLD_STATION,
        OLD_STATION_DEFAULT,
        props=(
            (
                STATION_BENCH,
                STATION_BENCH_DEFAULT,
            ),
        ),
    )


def test_compile_default_station_production_profile() -> None:
    spec = compile_default()

    assert spec.world_id == "studio_world"
    assert spec.location_id == "old_station"
    assert spec.variant_id == "default"

    assert (
        spec.production_profile_id
        == "studio_world_old_station_default_v1"
    )

    assert (
        spec.layout_profile
        is LocationLayoutProfile.OLD_STATION_PLATFORM_V1
    )

    assert (
        spec.architecture_profile
        is ArchitectureProfile.OLD_STATION_CANOPY_V1
    )

    assert (
        spec.depth_profile
        is EnvironmentDepthProfile.STATION_LAYERED_2_5D_V1
    )


def test_default_station_uses_dry_neutral_environment_state() -> None:
    spec = compile_default()

    assert (
        spec.surface_profile
        is SurfaceStateProfile.PLATFORM_DRY_V1
    )

    assert (
        spec.atmosphere_profile
        is AtmosphereStateProfile.DAY_NEUTRAL_V1
    )


def test_rainy_night_changes_state_without_changing_location_identity() -> None:
    spec = compile_world_production(
        STUDIO_WORLD,
        OLD_STATION,
        OLD_STATION_RAINY_NIGHT,
    )

    assert spec.world_id == "studio_world"
    assert spec.location_id == "old_station"
    assert spec.variant_id == "rainy_night"

    assert (
        spec.surface_profile
        is SurfaceStateProfile.PLATFORM_WET_V1
    )

    assert (
        spec.atmosphere_profile
        is AtmosphereStateProfile.RAINY_NIGHT_V1
    )


def test_station_bench_compiles_as_separate_prop_production_spec() -> None:
    spec = compile_default()

    assert len(
        spec.prop_specs
    ) == 1

    prop = spec.prop_specs[0]

    assert prop.world_id == "studio_world"
    assert prop.prop_id == "station_bench"
    assert prop.variant_id == "default"

    assert (
        prop.geometry_profile
        is PropGeometryProfile.STATION_BENCH_V1
    )


def test_prop_identity_is_stable_inside_world_production() -> None:
    first = compile_default()
    second = compile_default()

    assert first.prop_specs == second.prop_specs

    assert (
        first.prop_specs[0].prop_id
        == STATION_BENCH.prop_id
    )


def test_world_compiler_is_deterministic() -> None:
    assert compile_default() == compile_default()


def test_compiler_rejects_location_from_different_world() -> None:
    wrong_location = LocationIdentity(
        world_id="other_world",
        location_id="old_station",
        display_name="Wrong Station",
        summary="Wrong world.",
        anchors=(
            "wrong",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="does not belong",
    ):
        compile_world_production(
            STUDIO_WORLD,
            wrong_location,
            LocationVariant(
                world_id="other_world",
                location_id="old_station",
                variant_id="default",
                display_name="Wrong",
                summary="Wrong",
                descriptors=(
                    "wrong",
                ),
            ),
        )


def test_compiler_rejects_variant_from_different_location() -> None:
    variant = LocationVariant(
        world_id="studio_world",
        location_id="other_station",
        variant_id="default",
        display_name="Other",
        summary="Other location.",
        descriptors=(
            "other",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="does not belong",
    ):
        compile_world_production(
            STUDIO_WORLD,
            OLD_STATION,
            variant,
        )


def test_compiler_rejects_prop_from_different_world() -> None:
    prop = PropIdentity(
        world_id="other_world",
        prop_id="station_bench",
        display_name="Wrong Bench",
        summary="Wrong world.",
        anchors=(
            "bench",
        ),
    )

    variant = PropVariant(
        world_id="other_world",
        prop_id="station_bench",
        variant_id="default",
        display_name="Wrong Bench",
        summary="Wrong world.",
        descriptors=(
            "bench",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="different world",
    ):
        compile_world_production(
            STUDIO_WORLD,
            OLD_STATION,
            OLD_STATION_DEFAULT,
            props=(
                (
                    prop,
                    variant,
                ),
            ),
        )


def test_compiler_rejects_prop_variant_from_different_identity() -> None:
    variant = PropVariant(
        world_id="studio_world",
        prop_id="different_prop",
        variant_id="default",
        display_name="Different",
        summary="Different prop.",
        descriptors=(
            "different",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="does not belong",
    ):
        compile_world_production(
            STUDIO_WORLD,
            OLD_STATION,
            OLD_STATION_DEFAULT,
            props=(
                (
                    STATION_BENCH,
                    variant,
                ),
            ),
        )


def test_compiler_rejects_unsupported_location() -> None:
    location = LocationIdentity(
        world_id="studio_world",
        location_id="city_square",
        display_name="City Square",
        summary="Not implemented yet.",
        anchors=(
            "square",
        ),
    )

    variant = LocationVariant(
        world_id="studio_world",
        location_id="city_square",
        variant_id="default",
        display_name="City Square",
        summary="Not implemented.",
        descriptors=(
            "square",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="Unsupported world production selection",
    ):
        compile_world_production(
            STUDIO_WORLD,
            location,
            variant,
        )


def test_compiler_rejects_unsupported_location_variant() -> None:
    variant = LocationVariant(
        world_id="studio_world",
        location_id="old_station",
        variant_id="festival",
        display_name="Station Festival",
        summary="Not implemented.",
        descriptors=(
            "festival decorations",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="Unsupported location production variant",
    ):
        compile_world_production(
            STUDIO_WORLD,
            OLD_STATION,
            variant,
        )


def test_compiler_rejects_unsupported_prop() -> None:
    prop = PropIdentity(
        world_id="studio_world",
        prop_id="ticket_machine",
        display_name="Ticket Machine",
        summary="Not implemented yet.",
        anchors=(
            "machine",
        ),
    )

    variant = PropVariant(
        world_id="studio_world",
        prop_id="ticket_machine",
        variant_id="default",
        display_name="Ticket Machine",
        summary="Not implemented yet.",
        descriptors=(
            "machine",
        ),
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="Unsupported prop production selection",
    ):
        compile_world_production(
            STUDIO_WORLD,
            OLD_STATION,
            OLD_STATION_DEFAULT,
            props=(
                (
                    prop,
                    variant,
                ),
            ),
        )


def test_world_production_specs_are_immutable() -> None:
    spec = compile_default()

    with pytest.raises(
        FrozenInstanceError
    ):
        spec.location_id = "changed"


def test_world_production_contract_contains_no_raw_geometry_fields() -> None:
    world_fields = {
        item.name
        for item in fields(
            WorldProductionSpec
        )
    }

    prop_fields = {
        item.name
        for item in fields(
            PropProductionSpec
        )
    }

    forbidden = {
        "coordinates",
        "location",
        "rotation",
        "scale",
        "vertices",
        "faces",
        "mesh_path",
        "blend_path",
        "texture_path",
        "python_code",
    }

    assert world_fields.isdisjoint(
        forbidden
    )

    assert prop_fields.isdisjoint(
        forbidden
    )


def test_world_production_module_is_pure_and_safe() -> None:
    source = SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "import bpy",
        "from bpy",
        "kernel.adapters",
        "kernel.application",
        "pathlib",
        "subprocess",
        "pydantic",
        "eval(",
        "exec(",
        "os.system",
    )

    for token in forbidden:
        assert token not in source

def test_world_production_serialization_round_trip() -> None:
    from kernel.worlds import (
        world_production_from_data,
        world_production_to_data,
    )

    spec = compile_default()

    assert (
        world_production_from_data(
            world_production_to_data(
                spec
            )
        )
        == spec
    )


def test_rainy_world_serialization_round_trip() -> None:
    from kernel.worlds import (
        world_production_from_json,
        world_production_to_json,
    )

    spec = compile_world_production(
        STUDIO_WORLD,
        OLD_STATION,
        OLD_STATION_RAINY_NIGHT,
        props=(
            (
                STATION_BENCH,
                STATION_BENCH_DEFAULT,
            ),
        ),
    )

    assert (
        world_production_from_json(
            world_production_to_json(
                spec
            )
        )
        == spec
    )


def test_world_production_json_is_deterministic_and_versioned() -> None:
    import json

    from kernel.worlds import (
        WORLD_PRODUCTION_FILENAME,
        WORLD_PRODUCTION_SCHEMA_VERSION,
        world_production_to_json,
    )

    first = world_production_to_json(
        compile_default()
    )

    second = world_production_to_json(
        compile_default()
    )

    assert first == second

    data = json.loads(
        first
    )

    assert (
        data[
            "schema_version"
        ]
        == WORLD_PRODUCTION_SCHEMA_VERSION
        == 1
    )

    assert (
        WORLD_PRODUCTION_FILENAME
        == "world_production.json"
    )


def test_world_production_from_data_rejects_extra_top_level_field() -> None:
    from kernel.worlds import (
        WorldProductionSpecError,
        world_production_from_data,
        world_production_to_data,
    )

    data = world_production_to_data(
        compile_default()
    )

    data[
        "unexpected"
    ] = True

    with pytest.raises(
        WorldProductionSpecError,
        match="invalid fields",
    ):
        world_production_from_data(
            data
        )


def test_world_production_from_data_rejects_wrong_schema_version() -> None:
    from kernel.worlds import (
        WorldProductionSpecError,
        world_production_from_data,
        world_production_to_data,
    )

    data = world_production_to_data(
        compile_default()
    )

    data[
        "schema_version"
    ] = 999

    with pytest.raises(
        WorldProductionSpecError,
        match="schema version",
    ):
        world_production_from_data(
            data
        )


def test_world_production_from_data_rejects_invalid_profile() -> None:
    from kernel.worlds import (
        WorldProductionSpecError,
        world_production_from_data,
        world_production_to_data,
    )

    data = world_production_to_data(
        compile_default()
    )

    data[
        "layout_profile"
    ] = "arbitrary_ai_geometry"

    with pytest.raises(
        WorldProductionSpecError,
        match="Invalid world production profile",
    ):
        world_production_from_data(
            data
        )


def test_world_production_from_json_rejects_invalid_json() -> None:
    from kernel.worlds import (
        WorldProductionSpecError,
        world_production_from_json,
    )

    with pytest.raises(
        WorldProductionSpecError,
        match="Invalid world production JSON",
    ):
        world_production_from_json(
            "{not valid json"
        )


def test_prop_manifest_round_trip_preserves_profile() -> None:
    from kernel.worlds import (
        prop_production_from_data,
        prop_production_to_data,
    )

    prop = compile_default().prop_specs[
        0
    ]

    restored = prop_production_from_data(
        prop_production_to_data(
            prop
        )
    )

    assert restored == prop

    assert (
        restored.geometry_profile
        is PropGeometryProfile.STATION_BENCH_V1
    )
