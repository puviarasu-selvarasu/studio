"""Structural tests for Studio's trusted Blender world builder."""

from __future__ import annotations

import ast
from pathlib import Path


SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "world_builder.py"
)


def _source() -> str:
    return SOURCE.read_text(
        encoding="utf-8"
    )


def test_world_builder_consumes_bounded_world_production_spec() -> None:
    source = _source()

    assert (
        "WorldProductionSpec"
        in source
    )

    assert (
        "def build_world("
        in source
    )

    assert (
        "spec: WorldProductionSpec"
        in source
    )


def test_world_builder_exposes_built_world_categories() -> None:
    source = _source()

    required = (
        "class BuiltWorld",
        "platform_parts",
        "rail_parts",
        "architecture_parts",
        "prop_parts",
        "render_parts",
    )

    for token in required:
        assert token in source


def test_world_builder_contains_station_semantic_geometry() -> None:
    source = _source()

    required = (
        "_Platform",
        "_Platform_Safety",
        "_Rail_Left",
        "_Rail_Right",
        "_Sleeper_",
        "_Canopy_Roof",
        "_Column_",
        "_Station_Sign",
    )

    for token in required:
        assert token in source


def test_world_builder_supports_station_bench_profile() -> None:
    source = _source()

    required = (
        "STATION_BENCH_V1",
        "_Prop_station_bench",
        "_Seat",
        "_Back",
        "_Leg_L",
        "_Leg_R",
    )

    for token in required:
        assert token in source


def test_world_builder_uses_only_bounded_environment_state_profiles() -> None:
    source = _source()

    assert (
        "SurfaceStateProfile.PLATFORM_DRY_V1"
        in source
    )

    assert (
        "SurfaceStateProfile.PLATFORM_WET_V1"
        in source
    )

    assert (
        "AtmosphereStateProfile.DAY_NEUTRAL_V1"
        in source
    )

    assert (
        "AtmosphereStateProfile.RAINY_NIGHT_V1"
        in source
    )


def test_world_builder_does_not_reimplement_phase5_background_depth() -> None:
    source = _source()

    assert (
        "Phase 5 remains responsible "
        "for generic 2.5D background depth"
        in source
    )

    forbidden = (
        "StudioBackgroundNear",
        "StudioBackgroundMid",
        "StudioBackgroundFar",
        "apply_layered_background",
    )

    for token in forbidden:
        assert token not in source


def test_world_builder_contains_no_ai_or_dynamic_execution() -> None:
    source = _source()

    forbidden = (
        "Ollama",
        "LLM",
        "eval(",
        "exec(",
        "subprocess",
        "os.system",
    )

    for token in forbidden:
        assert token not in source


def test_world_builder_uses_lightweight_cube_geometry_only() -> None:
    source = _source()

    tree = ast.parse(
        source
    )

    def qualified_name(
        node: ast.AST,
    ) -> str | None:
        parts: list[str] = []

        current = node

        while isinstance(
            current,
            ast.Attribute,
        ):
            parts.append(
                current.attr
            )

            current = current.value

        if not isinstance(
            current,
            ast.Name,
        ):
            return None

        parts.append(
            current.id
        )

        return ".".join(
            reversed(
                parts
            )
        )

    primitive_calls = []

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        name = qualified_name(
            node.func
        )

        if (
            name is not None
            and name.startswith(
                "bpy.ops.mesh.primitive_"
            )
        ):
            primitive_calls.append(
                name
            )

    assert primitive_calls

    assert set(
        primitive_calls
    ) == {
        "bpy.ops.mesh.primitive_cube_add",
    }
