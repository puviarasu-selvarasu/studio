"""Contract tests for the Phase-13 anime render representation."""

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
    / "anime_render_proxy.py"
)


def _source() -> str:
    return SOURCE_PATH.read_text(
        encoding="utf-8"
    )


def test_phase13_has_explicit_retro_modern_style_profile() -> None:
    source = _source()

    assert (
        "class AnimeLookProfile"
        in source
    )

    assert (
        "RETRO_MODERN_CEL_V1"
        in source
    )


def test_phase13_uses_flat_planar_render_representation() -> None:
    source = _source()

    assert (
        "mesh.from_pydata"
        in source
    )

    assert (
        "primitive_cube_add"
        not in source
    )

    assert (
        "primitive_uv_sphere_add"
        not in source
    )


def test_phase13_contains_core_anime_face_language() -> None:
    source = _source()

    for token in (
        "AnimeProxy_UpperLash_",
        "AnimeProxy_EyeHighlight_",
        "AnimeProxy_NoseCue",
        "AnimeProxy_Mouth",
        "AnimeProxy_Fringe_",
        "AnimeProxy_FaceCelShadow",
    ):
        assert token in source


def test_phase13_has_retro_and_modern_cinematic_depth_language() -> None:
    source = _source()

    for token in (
        "sunset",
        "night",
        "AnimeProxy_CelestialDisc",
        "AnimeProxy_DistantSilhouette",
        "AnimeProxy_StationRoof",
    ):
        assert token in source


def test_phase13_stays_hardware_lightweight_and_safe() -> None:
    source = _source()

    for forbidden in (
        "geometry_nodes",
        "subdivision",
        "remesh",
        "bpy.ops.object.modifier_add",
        "subprocess",
    ):
        assert forbidden not in source.lower()

    tree = ast.parse(
        source
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
