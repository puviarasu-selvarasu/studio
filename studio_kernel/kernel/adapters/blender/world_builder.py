"""Trusted lightweight Blender realization of bounded world production."""

from __future__ import annotations

from dataclasses import dataclass

import bpy

from kernel.worlds.production import (
    ArchitectureProfile,
    AtmosphereStateProfile,
    EnvironmentDepthProfile,
    LocationLayoutProfile,
    PropGeometryProfile,
    PropProductionSpec,
    SurfaceStateProfile,
    WorldProductionSpec,
)


class WorldBuilderError(RuntimeError):
    """Represent unsupported trusted Blender world construction."""


@dataclass(
    frozen=True,
    slots=True,
)
class BuiltWorld:
    """Objects created for one bounded production-world realization."""

    platform_parts: tuple[bpy.types.Object, ...]
    rail_parts: tuple[bpy.types.Object, ...]
    architecture_parts: tuple[bpy.types.Object, ...]
    prop_parts: tuple[bpy.types.Object, ...]

    @property
    def render_parts(
        self,
    ) -> tuple[bpy.types.Object, ...]:
        """Return all location objects that participate in rendering."""

        return (
            self.platform_parts
            + self.rail_parts
            + self.architecture_parts
            + self.prop_parts
        )


@dataclass(
    frozen=True,
    slots=True,
)
class _WorldPalette:
    """Trusted Workbench material palette for one environment state."""

    platform: tuple[float, float, float, float]
    safety: tuple[float, float, float, float]
    rail: tuple[float, float, float, float]
    architecture: tuple[float, float, float, float]
    sign: tuple[float, float, float, float]
    bench: tuple[float, float, float, float]
    frame: tuple[float, float, float, float]


_DEFAULT_PALETTE = _WorldPalette(
    platform=(
        0.26,
        0.28,
        0.31,
        1.0,
    ),
    safety=(
        0.72,
        0.50,
        0.10,
        1.0,
    ),
    rail=(
        0.055,
        0.065,
        0.080,
        1.0,
    ),
    architecture=(
        0.34,
        0.36,
        0.39,
        1.0,
    ),
    sign=(
        0.52,
        0.10,
        0.08,
        1.0,
    ),
    bench=(
        0.28,
        0.18,
        0.10,
        1.0,
    ),
    frame=(
        0.055,
        0.060,
        0.070,
        1.0,
    ),
)


_RAINY_NIGHT_PALETTE = _WorldPalette(
    platform=(
        0.12,
        0.16,
        0.22,
        1.0,
    ),
    safety=(
        0.55,
        0.37,
        0.10,
        1.0,
    ),
    rail=(
        0.035,
        0.045,
        0.060,
        1.0,
    ),
    architecture=(
        0.14,
        0.18,
        0.25,
        1.0,
    ),
    sign=(
        0.60,
        0.15,
        0.10,
        1.0,
    ),
    bench=(
        0.20,
        0.14,
        0.11,
        1.0,
    ),
    frame=(
        0.035,
        0.045,
        0.060,
        1.0,
    ),
)


def _material(
    name: str,
    rgba: tuple[
        float,
        float,
        float,
        float,
    ],
) -> bpy.types.Material:
    """Return a deterministic lightweight material."""

    material = bpy.data.materials.get(
        name
    )

    if material is None:
        material = bpy.data.materials.new(
            name=name
        )

    material.diffuse_color = rgba

    return material


def _assign_material(
    obj: bpy.types.Object,
    material: bpy.types.Material,
) -> None:
    """Assign exactly one deterministic material."""

    obj.data.materials.clear()

    obj.data.materials.append(
        material
    )


def _create_box(
    *,
    name: str,
    location: tuple[
        float,
        float,
        float,
    ],
    dimensions: tuple[
        float,
        float,
        float,
    ],
    material: bpy.types.Material,
) -> bpy.types.Object:
    """Create one trusted low-cost art-directed cuboid."""

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location,
    )

    obj = bpy.context.active_object

    if obj is None:
        raise WorldBuilderError(
            "Unable to create world object: "
            + name
        )

    obj.name = name

    obj.dimensions = dimensions

    bpy.context.view_layer.objects.active = (
        obj
    )

    obj.select_set(
        True
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    obj.select_set(
        False
    )

    # Tiny bevels create line/value breaks while keeping
    # the underlying production geometry at eight vertices.
    bevel = obj.modifiers.new(
        name="StudioWorldBevel",
        type="BEVEL",
    )

    bevel.width = (
        min(dimensions)
        * 0.12
    )

    bevel.segments = 1

    # Bounded old-station production-design accents.
    if name.endswith(
        "_Canopy_Roof"
    ):
        obj.rotation_euler[0] = 0.055

    elif name.endswith(
        "_Prop_station_bench_Back"
    ):
        obj.rotation_euler[0] = -0.10

    elif (
        name.endswith(
            "_Station_Sign"
        )
        and "_Post_" not in name
    ):
        obj.rotation_euler[0] = 0.025

    _assign_material(
        obj,
        material,
    )

    return obj

def _palette_for(
    spec: WorldProductionSpec,
) -> _WorldPalette:
    """Resolve a bounded environment state into trusted material values."""

    if (
        spec.surface_profile
        is SurfaceStateProfile.PLATFORM_DRY_V1
        and spec.atmosphere_profile
        is AtmosphereStateProfile.DAY_NEUTRAL_V1
    ):
        return _DEFAULT_PALETTE

    if (
        spec.surface_profile
        is SurfaceStateProfile.PLATFORM_WET_V1
        and spec.atmosphere_profile
        is AtmosphereStateProfile.RAINY_NIGHT_V1
    ):
        return _RAINY_NIGHT_PALETTE

    raise WorldBuilderError(
        "Unsupported world surface/atmosphere profile combination."
    )


def _validate_station_profiles(
    spec: WorldProductionSpec,
) -> None:
    """Reject any production profile not implemented by this builder."""

    if (
        spec.world_id
        != "studio_world"
        or spec.location_id
        != "old_station"
    ):
        raise WorldBuilderError(
            "Unsupported world/location production selection."
        )

    if (
        spec.layout_profile
        is not LocationLayoutProfile.OLD_STATION_PLATFORM_V1
    ):
        raise WorldBuilderError(
            "Unsupported location layout profile."
        )

    if (
        spec.architecture_profile
        is not ArchitectureProfile.OLD_STATION_CANOPY_V1
    ):
        raise WorldBuilderError(
            "Unsupported architecture profile."
        )

    if (
        spec.depth_profile
        is not EnvironmentDepthProfile.STATION_LAYERED_2_5D_V1
    ):
        raise WorldBuilderError(
            "Unsupported environment depth profile."
        )


def _build_station_bench(
    *,
    prefix: str,
    spec: PropProductionSpec,
    bench_material: bpy.types.Material,
    frame_material: bpy.types.Material,
) -> tuple[bpy.types.Object, ...]:
    """Build the canonical lightweight station bench."""

    if (
        spec.geometry_profile
        is not PropGeometryProfile.STATION_BENCH_V1
    ):
        raise WorldBuilderError(
            "Unsupported prop geometry profile."
        )

    if (
        spec.world_id
        != "studio_world"
        or spec.prop_id
        != "station_bench"
        or spec.variant_id
        != "default"
    ):
        raise WorldBuilderError(
            "Unsupported station-bench production selection."
        )

    base = (
        prefix
        + "_Prop_station_bench"
    )

    seat = _create_box(
        name=base + "_Seat",
        location=(
            -2.45,
            0.75,
            0.62,
        ),
        dimensions=(
            1.80,
            0.44,
            0.14,
        ),
        material=bench_material,
    )

    back = _create_box(
        name=base + "_Back",
        location=(
            -2.45,
            0.96,
            1.07,
        ),
        dimensions=(
            1.80,
            0.12,
            0.72,
        ),
        material=bench_material,
    )

    left_leg = _create_box(
        name=base + "_Leg_L",
        location=(
            -3.05,
            0.75,
            0.30,
        ),
        dimensions=(
            0.12,
            0.32,
            0.58,
        ),
        material=frame_material,
    )

    right_leg = _create_box(
        name=base + "_Leg_R",
        location=(
            -1.85,
            0.75,
            0.30,
        ),
        dimensions=(
            0.12,
            0.32,
            0.58,
        ),
        material=frame_material,
    )

    return (
        seat,
        back,
        left_leg,
        right_leg,
    )


def build_world(
    spec: WorldProductionSpec,
) -> BuiltWorld:
    """Build one bounded reusable old-station production set."""

    if not isinstance(
        spec,
        WorldProductionSpec,
    ):
        raise WorldBuilderError(
            "spec must be WorldProductionSpec."
        )

    _validate_station_profiles(
        spec
    )

    palette = _palette_for(
        spec
    )

    prefix = (
        "StudioWorld_"
        + spec.world_id
        + "_"
        + spec.location_id
        + "_"
        + spec.variant_id
    )

    platform_material = _material(
        prefix + "_Material_Platform",
        palette.platform,
    )

    safety_material = _material(
        prefix + "_Material_Safety",
        palette.safety,
    )

    rail_material = _material(
        prefix + "_Material_Rail",
        palette.rail,
    )

    architecture_material = _material(
        prefix + "_Material_Architecture",
        palette.architecture,
    )

    sign_material = _material(
        prefix + "_Material_Sign",
        palette.sign,
    )

    bench_material = _material(
        prefix + "_Material_Bench",
        palette.bench,
    )

    frame_material = _material(
        prefix + "_Material_Frame",
        palette.frame,
    )

    # Location-specific production geometry only.
    # Phase 5 remains responsible for generic 2.5D background depth.

    platform = _create_box(
        name=prefix + "_Platform",
        location=(
            0.0,
            0.25,
            -0.16,
        ),
        dimensions=(
            10.0,
            6.4,
            0.32,
        ),
        material=platform_material,
    )

    safety_strip = _create_box(
        name=prefix + "_Platform_Safety",
        location=(
            0.0,
            3.18,
            0.025,
        ),
        dimensions=(
            10.0,
            0.16,
            0.05,
        ),
        material=safety_material,
    )

    platform_parts = (
        platform,
        safety_strip,
    )

    rail_left = _create_box(
        name=prefix + "_Rail_Left",
        location=(
            0.0,
            4.35,
            -0.02,
        ),
        dimensions=(
            10.0,
            0.09,
            0.11,
        ),
        material=rail_material,
    )

    rail_right = _create_box(
        name=prefix + "_Rail_Right",
        location=(
            0.0,
            5.35,
            -0.02,
        ),
        dimensions=(
            10.0,
            0.09,
            0.11,
        ),
        material=rail_material,
    )

    sleepers = tuple(
        _create_box(
            name=(
                prefix
                + "_Sleeper_"
                + f"{index:02d}"
            ),
            location=(
                x,
                4.85,
                -0.10,
            ),
            dimensions=(
                0.14,
                1.55,
                0.10,
            ),
            material=frame_material,
        )
        for index, x
        in enumerate(
            (
                -4.0,
                -2.4,
                -0.8,
                0.8,
                2.4,
                4.0,
            ),
            start=1,
        )
    )

    rail_parts = (
        rail_left,
        rail_right,
        *sleepers,
    )

    canopy = _create_box(
        name=prefix + "_Canopy_Roof",
        location=(
            0.0,
            1.20,
            3.72,
        ),
        dimensions=(
            8.8,
            3.25,
            0.18,
        ),
        material=architecture_material,
    )

    columns = tuple(
        _create_box(
            name=(
                prefix
                + "_Column_"
                + f"{index:02d}"
            ),
            location=(
                x,
                1.35,
                1.78,
            ),
            dimensions=(
                0.18,
                0.18,
                3.55,
            ),
            material=architecture_material,
        )
        for index, x
        in enumerate(
            (
                -3.6,
                -1.2,
                1.2,
                3.6,
            ),
            start=1,
        )
    )

    station_sign = _create_box(
        name=prefix + "_Station_Sign",
        location=(
            2.55,
            1.08,
            2.32,
        ),
        dimensions=(
            1.85,
            0.12,
            0.58,
        ),
        material=sign_material,
    )

    sign_post_left = _create_box(
        name=prefix + "_Station_Sign_Post_L",
        location=(
            1.88,
            1.08,
            1.18,
        ),
        dimensions=(
            0.10,
            0.10,
            2.28,
        ),
        material=frame_material,
    )

    sign_post_right = _create_box(
        name=prefix + "_Station_Sign_Post_R",
        location=(
            3.22,
            1.08,
            1.18,
        ),
        dimensions=(
            0.10,
            0.10,
            2.28,
        ),
        material=frame_material,
    )

    architecture_parts = (
        canopy,
        *columns,
        station_sign,
        sign_post_left,
        sign_post_right,
    )

    prop_parts: list[
        bpy.types.Object
    ] = []

    for prop_spec in spec.prop_specs:
        prop_parts.extend(
            _build_station_bench(
                prefix=prefix,
                spec=prop_spec,
                bench_material=bench_material,
                frame_material=frame_material,
            )
        )

    bpy.context.view_layer.update()

    return BuiltWorld(
        platform_parts=platform_parts,
        rail_parts=rail_parts,
        architecture_parts=architecture_parts,
        prop_parts=tuple(
            prop_parts
        ),
    )
