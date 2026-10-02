from __future__ import annotations

from pathlib import Path

import pytest

from kernel.characters.anime_2d_primitives import (
    Anime2DPrimitiveError,
    CelShadowShape,
    FillShape,
    InkStroke,
    Point2D,
    PrimitiveBundle,
    StrokeNode,
    arc_points,
    bounds,
    deterministic_wobble_points,
    make_cel_shadow,
    make_fill_shape,
    make_stroke,
    mirror_points,
    mirrored_closed_shape,
    polyline_length,
    scale_points,
    translate_points,
)


def test_point2d_rejects_non_finite_values() -> None:
    with pytest.raises(Anime2DPrimitiveError):
        Point2D(float("nan"), 0.0)

    with pytest.raises(Anime2DPrimitiveError):
        Point2D(0.0, float("inf"))


def test_stroke_node_requires_pressure_in_unit_interval() -> None:
    with pytest.raises(Anime2DPrimitiveError):
        StrokeNode(point=Point2D(0.0, 0.0), pressure=1.5)


def test_inkstroke_requires_two_nodes() -> None:
    with pytest.raises(Anime2DPrimitiveError):
        InkStroke(
            layer="ink",
            semantic_role="jaw",
            nodes=(StrokeNode(Point2D(0.0, 0.0), 1.0),),
            base_width=0.02,
        )


def test_fillshape_requires_three_points() -> None:
    with pytest.raises(Anime2DPrimitiveError):
        FillShape(
            layer="fill",
            semantic_role="face",
            color_key="skin",
            points=(Point2D(0.0, 0.0), Point2D(1.0, 0.0)),
        )


def test_celshadowshape_requires_unit_interval_opacity() -> None:
    with pytest.raises(Anime2DPrimitiveError):
        CelShadowShape(
            layer="shadow",
            semantic_role="cheek_shadow",
            shadow_key="skin_shadow",
            opacity=1.2,
            points=(
                Point2D(0.0, 0.0),
                Point2D(1.0, 0.0),
                Point2D(0.0, 1.0),
            ),
        )


def test_primitive_bundle_counts_all_primitives() -> None:
    stroke = make_stroke(
        layer="ink",
        semantic_role="jaw",
        points=(Point2D(0.0, 0.0), Point2D(1.0, 0.0)),
        base_width=0.03,
    )
    fill = make_fill_shape(
        layer="fill",
        semantic_role="face",
        color_key="skin",
        points=(
            Point2D(0.0, 0.0),
            Point2D(1.0, 0.0),
            Point2D(0.5, 1.0),
        ),
    )
    shadow = make_cel_shadow(
        layer="shadow",
        semantic_role="face_shadow",
        shadow_key="skin_shadow",
        opacity=0.7,
        points=(
            Point2D(0.0, 0.0),
            Point2D(1.0, 0.0),
            Point2D(0.5, 0.7),
        ),
    )

    bundle = PrimitiveBundle(
        strokes=(stroke,),
        fills=(fill,),
        shadows=(shadow,),
    )

    assert bundle.primitive_count == 3


def test_translate_and_scale_points_are_deterministic() -> None:
    points = (Point2D(1.0, 2.0), Point2D(3.0, 4.0))

    translated = translate_points(points, dx=2.0, dy=-1.0)
    scaled = scale_points(points, sx=2.0, sy=3.0)

    assert translated == (Point2D(3.0, 1.0), Point2D(5.0, 3.0))
    assert scaled == (Point2D(2.0, 6.0), Point2D(6.0, 12.0))


def test_mirror_points_reflects_across_axis() -> None:
    points = (Point2D(2.0, 1.0), Point2D(3.0, 2.0))

    mirrored = mirror_points(points, axis_x=1.0)

    assert mirrored == (Point2D(0.0, 1.0), Point2D(-1.0, 2.0))


def test_bounds_returns_min_max_extent() -> None:
    points = (
        Point2D(-1.0, 2.0),
        Point2D(3.0, -4.0),
        Point2D(2.5, 1.0),
    )

    assert bounds(points) == (-1.0, -4.0, 3.0, 2.0)


def test_polyline_length_computes_total_segment_length() -> None:
    points = (
        Point2D(0.0, 0.0),
        Point2D(3.0, 4.0),
        Point2D(6.0, 8.0),
    )

    assert polyline_length(points) == pytest.approx(10.0)


def test_arc_points_returns_expected_endpoints() -> None:
    points = arc_points(
        center=Point2D(0.0, 0.0),
        radius_x=2.0,
        radius_y=1.0,
        start_degrees=0.0,
        end_degrees=180.0,
        point_count=5,
    )

    assert len(points) == 5
    assert points[0].x == pytest.approx(2.0)
    assert points[0].y == pytest.approx(0.0)
    assert points[-1].x == pytest.approx(-2.0)
    assert points[-1].y == pytest.approx(0.0, abs=1e-8)


def test_mirrored_closed_shape_builds_symmetric_outline() -> None:
    half = (
        Point2D(0.0, 1.0),
        Point2D(1.0, 0.5),
        Point2D(0.0, -1.0),
    )

    result = mirrored_closed_shape(half, axis_x=0.0)

    assert result == (
        Point2D(0.0, 1.0),
        Point2D(1.0, 0.5),
        Point2D(0.0, -1.0),
        Point2D(-1.0, 0.5),
        Point2D(0.0, 1.0),
    )


def test_deterministic_wobble_is_repeatable_for_same_seed() -> None:
    points = (
        Point2D(0.0, 0.0),
        Point2D(1.0, 0.0),
        Point2D(2.0, 0.0),
    )

    first = deterministic_wobble_points(points, seed="jaw", amplitude=0.05)
    second = deterministic_wobble_points(points, seed="jaw", amplitude=0.05)
    third = deterministic_wobble_points(points, seed="brow", amplitude=0.05)

    assert first == second
    assert first != third
    assert first[0] == points[0]
    assert first[-1] == points[-1]


def test_make_stroke_supports_pressure_and_optional_wobble() -> None:
    stroke = make_stroke(
        layer="ink",
        semantic_role="upper_lash",
        points=(
            Point2D(0.0, 0.0),
            Point2D(0.5, 0.2),
            Point2D(1.0, 0.0),
        ),
        base_width=0.025,
        pressure_profile=(0.7, 1.0, 0.5),
        wobble_seed="upper_lash",
        wobble_amplitude=0.01,
    )

    assert isinstance(stroke, InkStroke)
    assert stroke.base_width == pytest.approx(0.025)
    assert stroke.pressures == (0.7, 1.0, 0.5)
    assert stroke.points[0] == Point2D(0.0, 0.0)
    assert stroke.points[-1] == Point2D(1.0, 0.0)


def test_make_fill_and_shadow_return_expected_types() -> None:
    fill = make_fill_shape(
        layer="fill",
        semantic_role="hair_mass",
        color_key="hair",
        points=(
            Point2D(0.0, 0.0),
            Point2D(1.0, 0.0),
            Point2D(0.6, 0.8),
        ),
    )
    shadow = make_cel_shadow(
        layer="shadow",
        semantic_role="hair_shadow",
        shadow_key="hair_shadow",
        opacity=0.65,
        points=(
            Point2D(0.1, 0.1),
            Point2D(0.8, 0.2),
            Point2D(0.4, 0.6),
        ),
    )

    assert isinstance(fill, FillShape)
    assert isinstance(shadow, CelShadowShape)
    assert shadow.opacity == pytest.approx(0.65)


def test_make_stroke_rejects_mismatched_pressure_profile_length() -> None:
    with pytest.raises(Anime2DPrimitiveError):
        make_stroke(
            layer="ink",
            semantic_role="brow",
            points=(Point2D(0.0, 0.0), Point2D(1.0, 0.0)),
            base_width=0.02,
            pressure_profile=(1.0, 0.8, 0.6),
        )


def test_phase15b_primitives_module_is_renderer_neutral() -> None:
    source_path = (
        Path(__file__).resolve().parents[1]
        / "kernel"
        / "characters"
        / "anime_2d_primitives.py"
    )
    source = source_path.read_text(encoding="utf-8").lower()

    assert "import bpy" not in source
    assert "primitive_cube_add" not in source
    assert "geometry_nodes" not in source
