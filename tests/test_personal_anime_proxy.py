from __future__ import annotations

import ast
from pathlib import Path


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


SOURCE_PATH = (
    ROOT
    / "studio_kernel"
    / "kernel"
    / "adapters"
    / "blender"
    / "personal_anime_proxy.py"
)


def _source() -> str:
    return SOURCE_PATH.read_text(
        encoding="utf-8"
    )


def test_renderer_consumes_generic_profile() -> None:
    source = _source()

    assert (
        "PersonalAnimeCaptureProfile"
        in source
    )

    assert (
        "build_personal_identity_proof"
        in source
    )


def test_renderer_supports_three_identity_views() -> None:
    source = _source()

    for token in (
        '"front"',
        '"profile"',
        '"full_body"',
    ):
        assert token in source


def test_renderer_is_not_hard_coded_to_one_person() -> None:
    source = _source().lower()

    assert "puvi" not in source
    assert "puviarasu" not in source


def test_renderer_responds_to_capture_parameters() -> None:
    source = _source()

    for token in (
        "profile.face_shape",
        "profile.hair_shape",
        "profile.hair_texture",
        "profile.brow_style",
        "profile.eye_shape",
        "profile.nose_profile",
        "profile.facial_hair_style",
        "profile.body_silhouette",
        "profile.shoulder_scale",
    ):
        assert token in source


def test_renderer_remains_lightweight_2d_geometry() -> None:
    source = _source().lower()

    assert (
        "mesh.from_pydata"
        in source
    )

    for forbidden in (
        "primitive_cube_add",
        "primitive_uv_sphere_add",
        "geometry_nodes",
        "subdivision",
        "remesh",
        "modifier_add",
        "subprocess",
    ):
        assert forbidden not in source


def test_renderer_has_no_dynamic_execution() -> None:
    tree = ast.parse(
        _source()
    )

    names = {
        node.id
        for node
        in ast.walk(tree)
        if isinstance(
            node,
            ast.Name,
        )
    }

    assert "eval" not in names
    assert "exec" not in names
