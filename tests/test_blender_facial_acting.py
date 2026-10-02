"""Contract tests for trusted Blender facial acting."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(
    __file__
).resolve().parents[
    1
]

EXECUTOR = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "facial_acting.py"
)


def _source() -> str:
    return EXECUTOR.read_text(
        encoding="utf-8"
    )


def test_facial_acting_reuses_canonical_face_parts() -> None:
    source = _source()

    for token in (
        '"Eye_L"',
        '"Eye_R"',
        '"Pupil_L"',
        '"Pupil_R"',
        '"Brow_L"',
        '"Brow_R"',
        '"Mouth"',
        "built_character.face_parts",
    ):
        assert token in source


def test_facial_acting_reuses_trusted_pose_controls() -> None:
    source = _source()

    assert (
        "set_bone_rotation_degrees"
        in source
    )

    assert (
        "insert_bone_rotation_keyframe"
        in source
    )

    assert '"head"' in source
    assert '"chest"' in source


def test_facial_acting_keyframes_mouth_blinks_and_brows() -> None:
    source = _source()

    assert (
        'data_path="scale"'
        in source
    )

    assert (
        'data_path="rotation_euler"'
        in source
    )

    assert "_MOUTH_SCALES" in source


def test_facial_acting_has_no_dynamic_execution_or_subprocess() -> None:
    source = _source()

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
    assert "subprocess" not in source
