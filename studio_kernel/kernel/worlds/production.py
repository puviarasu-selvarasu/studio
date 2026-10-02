"""Bounded deterministic production contracts for Studio worlds."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum

from .models import (
    LocationIdentity,
    LocationVariant,
    PropIdentity,
    PropVariant,
    WorldIdentity,
)


class WorldProductionSpecError(ValueError):
    """Represent invalid or unsupported world production data."""


_STABLE_ID = re.compile(
    r"^[a-z][a-z0-9_-]*$"
)


class LocationLayoutProfile(str, Enum):
    """Trusted reusable spatial-layout families."""

    OLD_STATION_PLATFORM_V1 = (
        "old_station_platform_v1"
    )


class ArchitectureProfile(str, Enum):
    """Trusted reusable architectural construction families."""

    OLD_STATION_CANOPY_V1 = (
        "old_station_canopy_v1"
    )


class EnvironmentDepthProfile(str, Enum):
    """Trusted 2.5D environment-depth organization."""

    STATION_LAYERED_2_5D_V1 = (
        "station_layered_2_5d_v1"
    )


class SurfaceStateProfile(str, Enum):
    """Bounded contextual surface state."""

    PLATFORM_DRY_V1 = (
        "platform_dry_v1"
    )

    PLATFORM_WET_V1 = (
        "platform_wet_v1"
    )


class AtmosphereStateProfile(str, Enum):
    """Bounded contextual atmosphere state."""

    DAY_NEUTRAL_V1 = (
        "day_neutral_v1"
    )

    RAINY_NIGHT_V1 = (
        "rainy_night_v1"
    )


class PropGeometryProfile(str, Enum):
    """Trusted reusable prop geometry family."""

    STATION_BENCH_V1 = (
        "station_bench_v1"
    )


def _required_id(
    value: str,
    *,
    label: str,
) -> str:
    """Validate one stable production identifier."""

    if not isinstance(
        value,
        str,
    ):
        raise WorldProductionSpecError(
            f"{label} must be a string."
        )

    normalized = value.strip()

    if (
        not normalized
        or _STABLE_ID.fullmatch(
            normalized
        )
        is None
    ):
        raise WorldProductionSpecError(
            f"{label} must be a stable lowercase identifier."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class PropProductionSpec:
    """Bounded production description of one selected story prop."""

    world_id: str
    prop_id: str
    variant_id: str
    production_profile_id: str
    geometry_profile: PropGeometryProfile

    def __post_init__(
        self,
    ) -> None:
        """Validate bounded prop production data."""

        for field_name in (
            "world_id",
            "prop_id",
            "variant_id",
            "production_profile_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_id(
                    getattr(
                        self,
                        field_name,
                    ),
                    label=field_name,
                ),
            )

        if not isinstance(
            self.geometry_profile,
            PropGeometryProfile,
        ):
            raise WorldProductionSpecError(
                "geometry_profile must be PropGeometryProfile."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class WorldProductionSpec:
    """Bounded production description of one reusable location state."""

    world_id: str
    location_id: str
    variant_id: str
    production_profile_id: str
    layout_profile: LocationLayoutProfile
    architecture_profile: ArchitectureProfile
    depth_profile: EnvironmentDepthProfile
    surface_profile: SurfaceStateProfile
    atmosphere_profile: AtmosphereStateProfile
    prop_specs: tuple[PropProductionSpec, ...] = ()

    def __post_init__(
        self,
    ) -> None:
        """Validate bounded world production data."""

        for field_name in (
            "world_id",
            "location_id",
            "variant_id",
            "production_profile_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_id(
                    getattr(
                        self,
                        field_name,
                    ),
                    label=field_name,
                ),
            )

        typed_profiles = (
            (
                self.layout_profile,
                LocationLayoutProfile,
                "layout_profile",
            ),
            (
                self.architecture_profile,
                ArchitectureProfile,
                "architecture_profile",
            ),
            (
                self.depth_profile,
                EnvironmentDepthProfile,
                "depth_profile",
            ),
            (
                self.surface_profile,
                SurfaceStateProfile,
                "surface_profile",
            ),
            (
                self.atmosphere_profile,
                AtmosphereStateProfile,
                "atmosphere_profile",
            ),
        )

        for (
            value,
            expected_type,
            label,
        ) in typed_profiles:
            if not isinstance(
                value,
                expected_type,
            ):
                raise WorldProductionSpecError(
                    f"{label} has an invalid profile type."
                )

        if not isinstance(
            self.prop_specs,
            tuple,
        ):
            raise WorldProductionSpecError(
                "prop_specs must be a tuple."
            )

        for spec in self.prop_specs:
            if not isinstance(
                spec,
                PropProductionSpec,
            ):
                raise WorldProductionSpecError(
                    "prop_specs contains an invalid value."
                )

            if (
                spec.world_id
                != self.world_id
            ):
                raise WorldProductionSpecError(
                    "Prop production world does not match location world."
                )

        prop_keys = [
            (
                spec.prop_id,
                spec.variant_id,
            )
            for spec
            in self.prop_specs
        ]

        if (
            len(
                set(
                    prop_keys
                )
            )
            != len(
                prop_keys
            )
        ):
            raise WorldProductionSpecError(
                "Duplicate prop production selection."
            )


def _compile_prop_production(
    identity: PropIdentity,
    variant: PropVariant,
    *,
    world_id: str,
) -> PropProductionSpec:
    """Compile one semantic prop selection into a trusted profile."""

    if not isinstance(
        identity,
        PropIdentity,
    ):
        raise WorldProductionSpecError(
            "Prop identity must be PropIdentity."
        )

    if not isinstance(
        variant,
        PropVariant,
    ):
        raise WorldProductionSpecError(
            "Prop variant must be PropVariant."
        )

    if (
        identity.world_id
        != world_id
    ):
        raise WorldProductionSpecError(
            "Prop identity belongs to a different world."
        )

    if (
        variant.world_id
        != identity.world_id
        or variant.prop_id
        != identity.prop_id
    ):
        raise WorldProductionSpecError(
            "Prop variant does not belong to prop identity."
        )

    if (
        identity.prop_id
        != "station_bench"
        or variant.variant_id
        != "default"
    ):
        raise WorldProductionSpecError(
            "Unsupported prop production selection: "
            + identity.prop_id
            + ":"
            + variant.variant_id
        )

    return PropProductionSpec(
        world_id=identity.world_id,
        prop_id=identity.prop_id,
        variant_id=variant.variant_id,
        production_profile_id=(
            "studio_world_station_bench_default_v1"
        ),
        geometry_profile=(
            PropGeometryProfile.STATION_BENCH_V1
        ),
    )


def compile_world_production(
    world: WorldIdentity,
    location: LocationIdentity,
    location_variant: LocationVariant,
    *,
    props: tuple[
        tuple[
            PropIdentity,
            PropVariant,
        ],
        ...,
    ] = (),
) -> WorldProductionSpec:
    """Compile semantic world selections into bounded production data."""

    if not isinstance(
        world,
        WorldIdentity,
    ):
        raise WorldProductionSpecError(
            "world must be WorldIdentity."
        )

    if not isinstance(
        location,
        LocationIdentity,
    ):
        raise WorldProductionSpecError(
            "location must be LocationIdentity."
        )

    if not isinstance(
        location_variant,
        LocationVariant,
    ):
        raise WorldProductionSpecError(
            "location_variant must be LocationVariant."
        )

    if (
        location.world_id
        != world.world_id
    ):
        raise WorldProductionSpecError(
            "Location does not belong to selected world."
        )

    if (
        location_variant.world_id
        != location.world_id
        or location_variant.location_id
        != location.location_id
    ):
        raise WorldProductionSpecError(
            "Location variant does not belong to selected location."
        )

    if (
        world.world_id
        != "studio_world"
        or location.location_id
        != "old_station"
    ):
        raise WorldProductionSpecError(
            "Unsupported world production selection: "
            + world.world_id
            + ":"
            + location.location_id
        )

    variant_profiles = {
        "default": (
            SurfaceStateProfile.PLATFORM_DRY_V1,
            AtmosphereStateProfile.DAY_NEUTRAL_V1,
        ),
        "rainy_night": (
            SurfaceStateProfile.PLATFORM_WET_V1,
            AtmosphereStateProfile.RAINY_NIGHT_V1,
        ),
    }

    profiles = variant_profiles.get(
        location_variant.variant_id
    )

    if profiles is None:
        raise WorldProductionSpecError(
            "Unsupported location production variant: "
            + location_variant.variant_id
        )

    if not isinstance(
        props,
        tuple,
    ):
        raise WorldProductionSpecError(
            "props must be a tuple."
        )

    compiled_props = []

    for selection in props:
        if (
            not isinstance(
                selection,
                tuple,
            )
            or len(
                selection
            )
            != 2
        ):
            raise WorldProductionSpecError(
                "Each prop selection must contain "
                "PropIdentity and PropVariant."
            )

        identity, variant = selection

        compiled_props.append(
            _compile_prop_production(
                identity,
                variant,
                world_id=world.world_id,
            )
        )

    surface_profile, atmosphere_profile = (
        profiles
    )

    return WorldProductionSpec(
        world_id=world.world_id,
        location_id=location.location_id,
        variant_id=location_variant.variant_id,
        production_profile_id=(
            world.world_id
            + "_"
            + location.location_id
            + "_"
            + location_variant.variant_id
            + "_v1"
        ),
        layout_profile=(
            LocationLayoutProfile.OLD_STATION_PLATFORM_V1
        ),
        architecture_profile=(
            ArchitectureProfile.OLD_STATION_CANOPY_V1
        ),
        depth_profile=(
            EnvironmentDepthProfile.STATION_LAYERED_2_5D_V1
        ),
        surface_profile=surface_profile,
        atmosphere_profile=atmosphere_profile,
        prop_specs=tuple(
            compiled_props
        ),
    )

WORLD_PRODUCTION_SCHEMA_VERSION = 1
WORLD_PRODUCTION_FILENAME = "world_production.json"


def prop_production_to_data(
    spec: PropProductionSpec,
) -> dict[str, object]:
    """Serialize one bounded prop production specification."""

    if not isinstance(
        spec,
        PropProductionSpec,
    ):
        raise WorldProductionSpecError(
            "spec must be PropProductionSpec."
        )

    return {
        "world_id": spec.world_id,
        "prop_id": spec.prop_id,
        "variant_id": spec.variant_id,
        "production_profile_id": spec.production_profile_id,
        "geometry_profile": spec.geometry_profile.value,
    }


def prop_production_from_data(
    data: object,
) -> PropProductionSpec:
    """Restore one strictly validated prop production specification."""

    if not isinstance(
        data,
        dict,
    ):
        raise WorldProductionSpecError(
            "Prop production data must be an object."
        )

    expected = {
        "world_id",
        "prop_id",
        "variant_id",
        "production_profile_id",
        "geometry_profile",
    }

    if set(
        data
    ) != expected:
        raise WorldProductionSpecError(
            "Prop production data has invalid fields."
        )

    try:
        geometry_profile = PropGeometryProfile(
            data[
                "geometry_profile"
            ]
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise WorldProductionSpecError(
            "Invalid prop geometry profile."
        ) from exc

    return PropProductionSpec(
        world_id=data[
            "world_id"
        ],
        prop_id=data[
            "prop_id"
        ],
        variant_id=data[
            "variant_id"
        ],
        production_profile_id=data[
            "production_profile_id"
        ],
        geometry_profile=geometry_profile,
    )


def world_production_to_data(
    spec: WorldProductionSpec,
) -> dict[str, object]:
    """Serialize one bounded world production specification."""

    if not isinstance(
        spec,
        WorldProductionSpec,
    ):
        raise WorldProductionSpecError(
            "spec must be WorldProductionSpec."
        )

    return {
        "schema_version": WORLD_PRODUCTION_SCHEMA_VERSION,
        "world_id": spec.world_id,
        "location_id": spec.location_id,
        "variant_id": spec.variant_id,
        "production_profile_id": spec.production_profile_id,
        "layout_profile": spec.layout_profile.value,
        "architecture_profile": spec.architecture_profile.value,
        "depth_profile": spec.depth_profile.value,
        "surface_profile": spec.surface_profile.value,
        "atmosphere_profile": spec.atmosphere_profile.value,
        "prop_specs": [
            prop_production_to_data(
                prop
            )
            for prop
            in spec.prop_specs
        ],
    }


def world_production_from_data(
    data: object,
) -> WorldProductionSpec:
    """Restore one strictly validated world production specification."""

    if not isinstance(
        data,
        dict,
    ):
        raise WorldProductionSpecError(
            "World production data must be an object."
        )

    expected = {
        "schema_version",
        "world_id",
        "location_id",
        "variant_id",
        "production_profile_id",
        "layout_profile",
        "architecture_profile",
        "depth_profile",
        "surface_profile",
        "atmosphere_profile",
        "prop_specs",
    }

    if set(
        data
    ) != expected:
        raise WorldProductionSpecError(
            "World production data has invalid fields."
        )

    if (
        data[
            "schema_version"
        ]
        != WORLD_PRODUCTION_SCHEMA_VERSION
    ):
        raise WorldProductionSpecError(
            "Unsupported world production schema version."
        )

    prop_data = data[
        "prop_specs"
    ]

    if not isinstance(
        prop_data,
        list,
    ):
        raise WorldProductionSpecError(
            "prop_specs must be a list."
        )

    try:
        layout_profile = LocationLayoutProfile(
            data[
                "layout_profile"
            ]
        )

        architecture_profile = ArchitectureProfile(
            data[
                "architecture_profile"
            ]
        )

        depth_profile = EnvironmentDepthProfile(
            data[
                "depth_profile"
            ]
        )

        surface_profile = SurfaceStateProfile(
            data[
                "surface_profile"
            ]
        )

        atmosphere_profile = AtmosphereStateProfile(
            data[
                "atmosphere_profile"
            ]
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise WorldProductionSpecError(
            "Invalid world production profile."
        ) from exc

    return WorldProductionSpec(
        world_id=data[
            "world_id"
        ],
        location_id=data[
            "location_id"
        ],
        variant_id=data[
            "variant_id"
        ],
        production_profile_id=data[
            "production_profile_id"
        ],
        layout_profile=layout_profile,
        architecture_profile=architecture_profile,
        depth_profile=depth_profile,
        surface_profile=surface_profile,
        atmosphere_profile=atmosphere_profile,
        prop_specs=tuple(
            prop_production_from_data(
                item
            )
            for item
            in prop_data
        ),
    )


def world_production_to_json(
    spec: WorldProductionSpec,
) -> str:
    """Serialize world production using deterministic human-readable JSON."""

    return (
        json.dumps(
            world_production_to_data(
                spec
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def world_production_from_json(
    payload: str,
) -> WorldProductionSpec:
    """Restore one world production manifest from strict JSON."""

    if not isinstance(
        payload,
        str,
    ):
        raise WorldProductionSpecError(
            "World production JSON must be a string."
        )

    try:
        data = json.loads(
            payload
        )
    except json.JSONDecodeError as exc:
        raise WorldProductionSpecError(
            "Invalid world production JSON."
        ) from exc

    return world_production_from_data(
        data
    )
