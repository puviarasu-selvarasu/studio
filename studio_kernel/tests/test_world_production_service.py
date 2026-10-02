"""Tests for Studio world-production application handoff."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.application.world_production_service import (
    WorldProductionService,
    WorldProductionServiceError,
)
from kernel.worlds import (
    AtmosphereStateProfile,
    PropGeometryProfile,
    SurfaceStateProfile,
)


SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "application"
    / "world_production_service.py"
)


def test_service_compiles_default_old_station() -> None:
    spec = (
        WorldProductionService()
        .compile_selection(
            "studio_world",
            "old_station",
        )
    )

    assert spec.world_id == "studio_world"
    assert spec.location_id == "old_station"
    assert spec.variant_id == "default"

    assert (
        spec.surface_profile
        is SurfaceStateProfile.PLATFORM_DRY_V1
    )


def test_service_compiles_station_with_bench() -> None:
    spec = (
        WorldProductionService()
        .compile_selection(
            "studio_world",
            "old_station",
            prop_selections=(
                (
                    "station_bench",
                    "default",
                ),
            ),
        )
    )

    assert len(
        spec.prop_specs
    ) == 1

    assert (
        spec.prop_specs[
            0
        ].geometry_profile
        is PropGeometryProfile.STATION_BENCH_V1
    )


def test_service_compiles_rainy_night_without_changing_location_identity() -> None:
    spec = (
        WorldProductionService()
        .compile_selection(
            "studio_world",
            "old_station",
            "rainy_night",
        )
    )

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


def test_service_rejects_unknown_world() -> None:
    with pytest.raises(
        WorldProductionServiceError,
        match="Unknown world_id",
    ):
        (
            WorldProductionService()
            .compile_selection(
                "missing_world",
                "old_station",
            )
        )


def test_service_rejects_unknown_location() -> None:
    with pytest.raises(
        WorldProductionServiceError,
        match="Unknown location_id",
    ):
        (
            WorldProductionService()
            .compile_selection(
                "studio_world",
                "missing_location",
            )
        )


def test_service_rejects_unknown_location_variant() -> None:
    with pytest.raises(
        WorldProductionServiceError,
        match="Unknown location variant",
    ):
        (
            WorldProductionService()
            .compile_selection(
                "studio_world",
                "old_station",
                "festival",
            )
        )


def test_service_rejects_unknown_prop() -> None:
    with pytest.raises(
        WorldProductionServiceError,
        match="Unknown prop_id",
    ):
        (
            WorldProductionService()
            .compile_selection(
                "studio_world",
                "old_station",
                prop_selections=(
                    (
                        "missing_prop",
                        "default",
                    ),
                ),
            )
        )


def test_service_rejects_unknown_prop_variant() -> None:
    with pytest.raises(
        WorldProductionServiceError,
        match="Unknown prop variant",
    ):
        (
            WorldProductionService()
            .compile_selection(
                "studio_world",
                "old_station",
                prop_selections=(
                    (
                        "station_bench",
                        "damaged",
                    ),
                ),
            )
        )


def test_service_remains_application_only_without_blender_or_ai() -> None:
    source = SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "bpy",
        "kernel.adapters",
        "Ollama",
        "LLM",
        "subprocess",
        "eval(",
        "exec(",
        "os.system",
    )

    for token in forbidden:
        assert token not in source
