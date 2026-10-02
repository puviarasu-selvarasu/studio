from __future__ import annotations

import ast
from pathlib import Path


ROOT = (
    Path(
        __file__
    )
    .resolve()
    .parents[
        1
    ]
)


SOURCE_PATH = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "retro_anime_cinematic.py"
)


def _source() -> str:
    return SOURCE_PATH.read_text(
        encoding="utf-8"
    )


def test_retro_cinematic_has_sunset_and_night_color_scripts() -> None:
    source = _source()

    assert "SUNSET" in source
    assert "NIGHT" in source


def test_retro_cinematic_has_layered_station_staging() -> None:
    source = _source()

    for token in (
        "StudioRetro_Sky",
        "StudioRetro_Horizon",
        "StudioRetro_Platform",
        "StudioRetro_Canopy",
        "StudioRetro_BenchSeat",
        "StudioRetro_ForegroundLeft",
    ):
        assert token in source


def test_retro_cinematic_supports_graphic_silhouette() -> None:
    source = _source()

    assert (
        "apply_character_silhouette"
        in source
    )

    assert (
        "StudioRetroCharacterSilhouette"
        in source
    )


def test_retro_cinematic_stays_hardware_lightweight() -> None:
    source = _source()

    assert (
        "primitive_cube_add"
        in source
    )

    assert (
        "primitive_uv_sphere_add"
        in source
    )

    for forbidden in (
        "geometry_nodes",
        "remesh",
        "subdivision",
        "bpy.ops.object.modifier_add",
    ):
        assert forbidden not in source.lower()


def test_retro_cinematic_has_no_dynamic_execution() -> None:
    tree = ast.parse(
        _source()
    )

    names = {
        node.id
        for node
        in ast.walk(
            tree
        )
        if isinstance(
            node,
            ast.Name,
        )
    }

    assert "eval" not in names
    assert "exec" not in names
