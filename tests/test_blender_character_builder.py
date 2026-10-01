"""Host-side structural tests for the trusted Blender character builder."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

BUILDER_PATH = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "character_builder.py"
)


def _source() -> str:
    return BUILDER_PATH.read_text(
        encoding="utf-8"
    )


def _tree() -> ast.Module:
    return ast.parse(
        _source()
    )


def test_character_builder_module_exists() -> None:
    assert BUILDER_PATH.is_file()


def test_character_builder_reuses_canonical_humanoid_rig() -> None:
    source = _source()

    assert "create_humanoid_armature" in source
    assert "parent_object_to_bone" in source


def test_character_builder_does_not_call_generic_debug_body() -> None:
    tree = _tree()

    called = {
        node.func.id
        for node in ast.walk(
            tree
        )
        if (
            isinstance(
                node,
                ast.Call,
            )
            and isinstance(
                node.func,
                ast.Name,
            )
        )
    }

    assert "create_debug_body" not in called


def test_character_builder_consumes_bounded_production_spec() -> None:
    source = _source()

    required = (
        "CharacterProductionSpec",
        "RigProfile.STUDIO_HUMANOID_V1",
        "BodyProfile.LIGHTWEIGHT_ANIME_V1",
        "HairProfile.SHOULDER_LENGTH_DARK_V1",
        "OutfitProfile.SIMPLE_EVERYDAY_V1",
        "CharacterPaletteProfile.MOMO_DEFAULT_V1",
    )

    for token in required:
        assert token in source


def test_character_builder_uses_only_lightweight_mesh_primitives() -> None:
    source = _source()

    assert "primitive_cube_add" in source
    assert "primitive_uv_sphere_add" in source

    forbidden = (
        "primitive_monkey_add",
        "bpy.ops.object.modifier_add",
        "subdivision",
        "remesh",
        "geometry_nodes",
    )

    for token in forbidden:
        assert token not in source.lower()


def test_character_builder_contains_no_dynamic_execution() -> None:
    source = _source()

    assert "eval(" not in source
    assert "exec(" not in source
    assert "subprocess" not in source
    assert "os.system" not in source


def test_character_builder_adds_lightweight_face_features() -> None:
    source = _source()

    required = (
        "face_parts",
        "_create_face_mark",
        "_Material_Face",
        'label="Eye_L"',
        'label="Eye_R"',
        'label="Mouth"',
    )

    for token in required:
        assert token in source


def test_character_builder_hair_no_longer_encloses_face() -> None:
    source = _source()
    tree = ast.parse(
        source
    )

    function = next(
        node
        for node in tree.body
        if (
            isinstance(
                node,
                ast.FunctionDef,
            )
            and node.name
            == "_create_hair_cap"
        )
    )

    lines = source.splitlines()

    segment = "\n".join(
        lines[
            function.lineno - 1:
            function.end_lineno
        ]
    )

    assert "primitive_cube_add" in segment
    assert "primitive_uv_sphere_add" not in segment
    assert "_Hair_Back" in segment
    assert "_create_hair_top" in source


def test_character_builder_adds_neutral_arm_presentation() -> None:
    source = _source()

    required = (
        "_apply_anime_neutral_pose",
        '"upper_arm.L": -0.92',
        '"upper_arm.R": -0.92',
        "rotation_euler[0]",
    )

    for token in required:
        assert token in source

    assert "rotation_euler[1]" not in source[
        source.index("def _apply_anime_neutral_pose"):
        source.index("def _create_segment")
    ]
