"""Renderer-neutral pure-2D drawing primitives for Studio.

Phase 15A defined the semantic art contract.
Phase 15B provides the small deterministic geometry primitives needed to
assemble hand-drawn-looking anime drawings without depending on any 3D API.

These primitives are intentionally generic and lightweight:
- points
- stroke nodes with pressure
- variable-width ink strokes
- filled shapes
- cel-shadow regions
- small geometry helpers

Later Phase-15 steps can use these primitives to build the actual front,
three-quarter and expression drawings.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math


class Anime2DPrimitiveError(ValueError):
    """Raised when a primitive or geometric helper receives invalid input."""


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Anime2DPrimitiveError(field + " must not be blank.")
    return value.strip()


def _finite(value: float, field: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise Anime2DPrimitiveError(field + " must be finite.")
    return number


def _unit_interval(value: float, field: str) -> float:
    number = _finite(value, field)
    if not 0.0 <= number <= 1.0:
        raise Anime2DPrimitiveError(field + " must be between 0.0 and 1.0.")
    return number


def _positive(value: float, field: str) -> float:
    number = _finite(value, field)
    if number <= 0.0:
        raise Anime2DPrimitiveError(field + " must be greater than zero.")
    return number


@dataclass(frozen=True, slots=True)
class Point2D:
    x: float
    y: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "x", _finite(self.x, "x"))
        object.__setattr__(self, "y", _finite(self.y, "y"))

    def translated(self, dx: float, dy: float) -> "Point2D":
        return Point2D(self.x + _finite(dx, "dx"), self.y + _finite(dy, "dy"))

    def scaled(self, sx: float, sy: float | None = None) -> "Point2D":
        scale_x = _finite(sx, "sx")
        scale_y = scale_x if sy is None else _finite(sy, "sy")
        return Point2D(self.x * scale_x, self.y * scale_y)

    def mirrored_x(self, axis_x: float = 0.0) -> "Point2D":
        axis = _finite(axis_x, "axis_x")
        return Point2D(axis + (axis - self.x), self.y)


@dataclass(frozen=True, slots=True)
class StrokeNode:
    point: Point2D
    pressure: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.point, Point2D):
            raise Anime2DPrimitiveError("point must be a Point2D.")
        object.__setattr__(self, "pressure", _unit_interval(self.pressure, "pressure"))


@dataclass(frozen=True, slots=True)
class InkStroke:
    layer: str
    semantic_role: str
    nodes: tuple[StrokeNode, ...]
    base_width: float
    closed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "layer", _required_text(self.layer, "layer"))
        object.__setattr__(
            self,
            "semantic_role",
            _required_text(self.semantic_role, "semantic_role"),
        )

        if not isinstance(self.nodes, tuple) or len(self.nodes) < 2:
            raise Anime2DPrimitiveError("InkStroke requires at least two nodes.")

        for node in self.nodes:
            if not isinstance(node, StrokeNode):
                raise Anime2DPrimitiveError("InkStroke nodes must be StrokeNode values.")

        object.__setattr__(self, "base_width", _positive(self.base_width, "base_width"))

    @property
    def pressures(self) -> tuple[float, ...]:
        return tuple(node.pressure for node in self.nodes)

    @property
    def points(self) -> tuple[Point2D, ...]:
        return tuple(node.point for node in self.nodes)


@dataclass(frozen=True, slots=True)
class FillShape:
    layer: str
    semantic_role: str
    color_key: str
    points: tuple[Point2D, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "layer", _required_text(self.layer, "layer"))
        object.__setattr__(
            self,
            "semantic_role",
            _required_text(self.semantic_role, "semantic_role"),
        )
        object.__setattr__(self, "color_key", _required_text(self.color_key, "color_key"))

        if not isinstance(self.points, tuple) or len(self.points) < 3:
            raise Anime2DPrimitiveError("FillShape requires at least three points.")

        for point in self.points:
            if not isinstance(point, Point2D):
                raise Anime2DPrimitiveError("FillShape points must be Point2D values.")


@dataclass(frozen=True, slots=True)
class CelShadowShape:
    layer: str
    semantic_role: str
    shadow_key: str
    opacity: float
    points: tuple[Point2D, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "layer", _required_text(self.layer, "layer"))
        object.__setattr__(
            self,
            "semantic_role",
            _required_text(self.semantic_role, "semantic_role"),
        )
        object.__setattr__(self, "shadow_key", _required_text(self.shadow_key, "shadow_key"))
        object.__setattr__(self, "opacity", _unit_interval(self.opacity, "opacity"))

        if not isinstance(self.points, tuple) or len(self.points) < 3:
            raise Anime2DPrimitiveError("CelShadowShape requires at least three points.")

        for point in self.points:
            if not isinstance(point, Point2D):
                raise Anime2DPrimitiveError(
                    "CelShadowShape points must be Point2D values."
                )


@dataclass(frozen=True, slots=True)
class PrimitiveBundle:
    strokes: tuple[InkStroke, ...] = ()
    fills: tuple[FillShape, ...] = ()
    shadows: tuple[CelShadowShape, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.strokes, tuple):
            raise Anime2DPrimitiveError("strokes must be a tuple.")
        if not isinstance(self.fills, tuple):
            raise Anime2DPrimitiveError("fills must be a tuple.")
        if not isinstance(self.shadows, tuple):
            raise Anime2DPrimitiveError("shadows must be a tuple.")

        for stroke in self.strokes:
            if not isinstance(stroke, InkStroke):
                raise Anime2DPrimitiveError("strokes must contain InkStroke values.")

        for fill in self.fills:
            if not isinstance(fill, FillShape):
                raise Anime2DPrimitiveError("fills must contain FillShape values.")

        for shadow in self.shadows:
            if not isinstance(shadow, CelShadowShape):
                raise Anime2DPrimitiveError(
                    "shadows must contain CelShadowShape values."
                )

    @property
    def primitive_count(self) -> int:
        return len(self.strokes) + len(self.fills) + len(self.shadows)


def polyline_length(points: tuple[Point2D, ...]) -> float:
    validated = _point_tuple(points, minimum=2, field="points")
    total = 0.0

    for current, following in zip(validated, validated[1:]):
        total += math.dist((current.x, current.y), (following.x, following.y))

    return total


def bounds(points: tuple[Point2D, ...]) -> tuple[float, float, float, float]:
    validated = _point_tuple(points, minimum=1, field="points")
    xs = tuple(point.x for point in validated)
    ys = tuple(point.y for point in validated)
    return (min(xs), min(ys), max(xs), max(ys))


def translate_points(
    points: tuple[Point2D, ...],
    dx: float,
    dy: float,
) -> tuple[Point2D, ...]:
    validated = _point_tuple(points, minimum=1, field="points")
    return tuple(point.translated(dx, dy) for point in validated)


def scale_points(
    points: tuple[Point2D, ...],
    sx: float,
    sy: float | None = None,
) -> tuple[Point2D, ...]:
    validated = _point_tuple(points, minimum=1, field="points")
    return tuple(point.scaled(sx, sy) for point in validated)


def mirror_points(
    points: tuple[Point2D, ...],
    *,
    axis_x: float = 0.0,
) -> tuple[Point2D, ...]:
    validated = _point_tuple(points, minimum=1, field="points")
    return tuple(point.mirrored_x(axis_x=axis_x) for point in validated)


def arc_points(
    *,
    center: Point2D,
    radius_x: float,
    radius_y: float,
    start_degrees: float,
    end_degrees: float,
    point_count: int,
) -> tuple[Point2D, ...]:
    if not isinstance(center, Point2D):
        raise Anime2DPrimitiveError("center must be a Point2D.")

    rx = _positive(radius_x, "radius_x")
    ry = _positive(radius_y, "radius_y")

    if not isinstance(point_count, int) or point_count < 2:
        raise Anime2DPrimitiveError("point_count must be an integer >= 2.")

    start = math.radians(_finite(start_degrees, "start_degrees"))
    end = math.radians(_finite(end_degrees, "end_degrees"))

    span = end - start
    if span == 0.0:
        raise Anime2DPrimitiveError("Arc span must not be zero.")

    result: list[Point2D] = []

    for index in range(point_count):
        t = index / (point_count - 1)
        angle = start + span * t
        result.append(
            Point2D(
                center.x + math.cos(angle) * rx,
                center.y + math.sin(angle) * ry,
            )
        )

    return tuple(result)


def mirrored_closed_shape(
    half_points: tuple[Point2D, ...],
    *,
    axis_x: float = 0.0,
) -> tuple[Point2D, ...]:
    validated = _point_tuple(half_points, minimum=2, field="half_points")
    mirrored = tuple(
        point.mirrored_x(axis_x=axis_x) for point in reversed(validated[:-1])
    )
    return validated + mirrored


def deterministic_wobble_points(
    points: tuple[Point2D, ...],
    *,
    seed: str,
    amplitude: float,
    keep_endpoints: bool = True,
) -> tuple[Point2D, ...]:
    validated = _point_tuple(points, minimum=1, field="points")
    seed_text = _required_text(seed, "seed")
    wobble = _finite(amplitude, "amplitude")

    if wobble < 0.0:
        raise Anime2DPrimitiveError("amplitude must be >= 0.0.")

    result: list[Point2D] = []

    for index, point in enumerate(validated):
        if keep_endpoints and index in {0, len(validated) - 1}:
            result.append(point)
            continue

        digest = hashlib.sha256(f"{seed_text}:{index}".encode("utf-8")).digest()
        dx_unit = int.from_bytes(digest[:8], "big") / (2**64 - 1)
        dy_unit = int.from_bytes(digest[8:16], "big") / (2**64 - 1)

        dx = (dx_unit * 2.0 - 1.0) * wobble
        dy = (dy_unit * 2.0 - 1.0) * wobble

        result.append(Point2D(point.x + dx, point.y + dy))

    return tuple(result)


def make_stroke(
    *,
    layer: str,
    semantic_role: str,
    points: tuple[Point2D, ...],
    base_width: float,
    pressure_profile: tuple[float, ...] | None = None,
    wobble_seed: str | None = None,
    wobble_amplitude: float = 0.0,
    closed: bool = False,
) -> InkStroke:
    validated_points = _point_tuple(points, minimum=2, field="points")

    if pressure_profile is None:
        pressures = tuple(1.0 for _ in validated_points)
    else:
        if not isinstance(pressure_profile, tuple):
            raise Anime2DPrimitiveError("pressure_profile must be a tuple when provided.")
        if len(pressure_profile) != len(validated_points):
            raise Anime2DPrimitiveError(
                "pressure_profile length must match point count."
            )
        pressures = tuple(
            _unit_interval(value, "pressure_profile item")
            for value in pressure_profile
        )

    if wobble_seed is not None:
        validated_points = deterministic_wobble_points(
            validated_points,
            seed=wobble_seed,
            amplitude=wobble_amplitude,
            keep_endpoints=True,
        )

    nodes = tuple(
        StrokeNode(point=point, pressure=pressure)
        for point, pressure in zip(validated_points, pressures)
    )

    return InkStroke(
        layer=layer,
        semantic_role=semantic_role,
        nodes=nodes,
        base_width=base_width,
        closed=closed,
    )


def make_fill_shape(
    *,
    layer: str,
    semantic_role: str,
    color_key: str,
    points: tuple[Point2D, ...],
) -> FillShape:
    return FillShape(
        layer=layer,
        semantic_role=semantic_role,
        color_key=color_key,
        points=_point_tuple(points, minimum=3, field="points"),
    )


def make_cel_shadow(
    *,
    layer: str,
    semantic_role: str,
    shadow_key: str,
    opacity: float,
    points: tuple[Point2D, ...],
) -> CelShadowShape:
    return CelShadowShape(
        layer=layer,
        semantic_role=semantic_role,
        shadow_key=shadow_key,
        opacity=opacity,
        points=_point_tuple(points, minimum=3, field="points"),
    )


def _point_tuple(
    points: tuple[Point2D, ...],
    *,
    minimum: int,
    field: str,
) -> tuple[Point2D, ...]:
    if not isinstance(points, tuple) or len(points) < minimum:
        raise Anime2DPrimitiveError(
            field
            + " must be a tuple containing at least "
            + str(minimum)
            + " Point2D values."
        )

    for point in points:
        if not isinstance(point, Point2D):
            raise Anime2DPrimitiveError(field + " must only contain Point2D values.")

    return points
