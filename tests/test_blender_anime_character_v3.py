"""Contract tests for Studio Human Anime Character V3."""

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
    / "anime_character_v3.py"
)


def _source() -> str:
    return SOURCE_PATH.read_text(
        encoding="utf-8"
    )


def test_human_anime_v3_reuses_canonical_character() -> None:
    source = _source()

    assert (
        "BuiltCharacter"
        in source
    )

    assert (
        "built_character.face_parts"
        in source
    )

    assert (
        "built_character.hair_parts"
        in source
    )


def test_human_anime_v3_keeps_canonical_expression_parts() -> None:
    source = _source()

    for token in (
        '"Eye_L"',
        '"Eye_R"',
        '"Pupil_L"',
        '"Pupil_R"',
        '"Brow_L"',
        '"Brow_R"',
        '"Mouth"',
    ):
        assert token in source


def test_human_anime_v3_adds_anime_face_language() -> None:
    source = _source()

    assert (
        "_replace_with_almond"
        in source
    )

    assert (
        "_replace_with_tapered_brow"
        in source
    )

    assert (
        "_replace_with_mouth_shape"
        in source
    )

    assert (
        "_AnimeV3_Nose"
        in source
    )

    assert (
        "_AnimeV3_Ear_L"
        in source
    )

    assert (
        "_AnimeV3_Ear_R"
        in source
    )


def test_human_anime_v3_replaces_block_fringe_with_pointed_strands() -> None:
    source = _source()

    assert (
        "_AnimeV3_Fringe_"
        in source
    )

    assert (
        '"fringe" in lowered'
        in source
    )

    assert (
        "hair.hide_render = True"
        in source
    )


def test_human_anime_v3_uses_lightweight_meshes_only() -> None:
    source = _source()

    assert (
        "from_pydata"
        in source
    )

    assert (
        "geometry_nodes"
        not in source
    )

    assert (
        "subdivision"
        not in source.lower()
    )

    assert (
        "remesh"
        not in source.lower()
    )

    assert (
        "bpy.ops.object.modifier_add"
        not in source
    )


def test_human_anime_v3_has_no_dynamic_execution() -> None:
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
    assert "subprocess" not in names
