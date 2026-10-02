"""Pure catalog and canonical semantic world data for Studio."""

from __future__ import annotations

from dataclasses import dataclass

from .models import (
    LocationIdentity,
    LocationVariant,
    PropIdentity,
    PropVariant,
    WorldIdentity,
)


class WorldCatalogError(ValueError):
    """Represent an invalid world, location, or prop catalog."""


@dataclass(
    frozen=True,
    slots=True,
)
class WorldCatalog:
    """Hold persistent worlds, locations, variants, and props."""

    worlds: tuple[WorldIdentity, ...] = ()
    locations: tuple[LocationIdentity, ...] = ()
    location_variants: tuple[LocationVariant, ...] = ()
    props: tuple[PropIdentity, ...] = ()
    prop_variants: tuple[PropVariant, ...] = ()

    def __post_init__(
        self,
    ) -> None:
        """Validate catalog types, uniqueness, and referential integrity."""

        collections = (
            (
                "worlds",
                self.worlds,
                WorldIdentity,
            ),
            (
                "locations",
                self.locations,
                LocationIdentity,
            ),
            (
                "location_variants",
                self.location_variants,
                LocationVariant,
            ),
            (
                "props",
                self.props,
                PropIdentity,
            ),
            (
                "prop_variants",
                self.prop_variants,
                PropVariant,
            ),
        )

        for (
            label,
            values,
            expected_type,
        ) in collections:
            if not isinstance(
                values,
                tuple,
            ):
                raise WorldCatalogError(
                    f"{label} must be a tuple."
                )

            for value in values:
                if not isinstance(
                    value,
                    expected_type,
                ):
                    raise WorldCatalogError(
                        f"{label} contains an invalid value."
                    )

        world_ids = [
            world.world_id
            for world
            in self.worlds
        ]

        if (
            len(
                set(
                    world_ids
                )
            )
            != len(
                world_ids
            )
        ):
            raise WorldCatalogError(
                "Duplicate world_id in catalog."
            )

        location_keys = [
            (
                location.world_id,
                location.location_id,
            )
            for location
            in self.locations
        ]

        if (
            len(
                set(
                    location_keys
                )
            )
            != len(
                location_keys
            )
        ):
            raise WorldCatalogError(
                "Duplicate location identity in catalog."
            )

        location_variant_keys = [
            (
                variant.world_id,
                variant.location_id,
                variant.variant_id,
            )
            for variant
            in self.location_variants
        ]

        if (
            len(
                set(
                    location_variant_keys
                )
            )
            != len(
                location_variant_keys
            )
        ):
            raise WorldCatalogError(
                "Duplicate location variant in catalog."
            )

        prop_keys = [
            (
                prop.world_id,
                prop.prop_id,
            )
            for prop
            in self.props
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
            raise WorldCatalogError(
                "Duplicate prop identity in catalog."
            )

        prop_variant_keys = [
            (
                variant.world_id,
                variant.prop_id,
                variant.variant_id,
            )
            for variant
            in self.prop_variants
        ]

        if (
            len(
                set(
                    prop_variant_keys
                )
            )
            != len(
                prop_variant_keys
            )
        ):
            raise WorldCatalogError(
                "Duplicate prop variant in catalog."
            )

        known_worlds = set(
            world_ids
        )

        known_locations = set(
            location_keys
        )

        known_props = set(
            prop_keys
        )

        for location in self.locations:
            if (
                location.world_id
                not in known_worlds
            ):
                raise WorldCatalogError(
                    "Location references an unknown world: "
                    + location.world_id
                )

        for variant in self.location_variants:
            key = (
                variant.world_id,
                variant.location_id,
            )

            if key not in known_locations:
                raise WorldCatalogError(
                    "Location variant references "
                    "an unknown location: "
                    + variant.world_id
                    + ":"
                    + variant.location_id
                )

        for prop in self.props:
            if (
                prop.world_id
                not in known_worlds
            ):
                raise WorldCatalogError(
                    "Prop references an unknown world: "
                    + prop.world_id
                )

        for variant in self.prop_variants:
            key = (
                variant.world_id,
                variant.prop_id,
            )

            if key not in known_props:
                raise WorldCatalogError(
                    "Prop variant references an unknown prop: "
                    + variant.world_id
                    + ":"
                    + variant.prop_id
                )

    def get_world(
        self,
        world_id: str,
    ) -> WorldIdentity | None:
        """Return one persistent world identity."""

        return next(
            (
                world
                for world in self.worlds
                if world.world_id
                == world_id
            ),
            None,
        )

    def get_location(
        self,
        world_id: str,
        location_id: str,
    ) -> LocationIdentity | None:
        """Return one persistent location identity."""

        return next(
            (
                location
                for location
                in self.locations
                if (
                    location.world_id
                    == world_id
                    and location.location_id
                    == location_id
                )
            ),
            None,
        )

    def get_location_variant(
        self,
        world_id: str,
        location_id: str,
        variant_id: str = "default",
    ) -> LocationVariant | None:
        """Return one contextual location presentation."""

        return next(
            (
                variant
                for variant
                in self.location_variants
                if (
                    variant.world_id
                    == world_id
                    and variant.location_id
                    == location_id
                    and variant.variant_id
                    == variant_id
                )
            ),
            None,
        )

    def locations_for(
        self,
        world_id: str,
    ) -> tuple[LocationIdentity, ...]:
        """Return all persistent locations in one world."""

        return tuple(
            location
            for location
            in self.locations
            if (
                location.world_id
                == world_id
            )
        )

    def get_prop(
        self,
        world_id: str,
        prop_id: str,
    ) -> PropIdentity | None:
        """Return one persistent prop identity."""

        return next(
            (
                prop
                for prop
                in self.props
                if (
                    prop.world_id
                    == world_id
                    and prop.prop_id
                    == prop_id
                )
            ),
            None,
        )

    def get_prop_variant(
        self,
        world_id: str,
        prop_id: str,
        variant_id: str = "default",
    ) -> PropVariant | None:
        """Return one contextual prop presentation."""

        return next(
            (
                variant
                for variant
                in self.prop_variants
                if (
                    variant.world_id
                    == world_id
                    and variant.prop_id
                    == prop_id
                    and variant.variant_id
                    == variant_id
                )
            ),
            None,
        )

    def props_for(
        self,
        world_id: str,
    ) -> tuple[PropIdentity, ...]:
        """Return all persistent props registered in one world."""

        return tuple(
            prop
            for prop
            in self.props
            if (
                prop.world_id
                == world_id
            )
        )


STUDIO_WORLD = WorldIdentity(
    world_id="studio_world",
    display_name="Studio World",
    summary=(
        "A grounded contemporary fictional setting designed "
        "for reusable anime production."
    ),
    anchors=(
        "grounded contemporary architecture",
        "restrained technology",
        "consistent regional visual language",
        "readable layered environments",
    ),
)


OLD_STATION = LocationIdentity(
    world_id="studio_world",
    location_id="old_station",
    display_name="Old Railway Station",
    summary=(
        "An aged but functioning railway station built around "
        "a long platform and a recognizable canopy silhouette."
    ),
    anchors=(
        "long central platform",
        "aged station canopy",
        "recognizable station name board",
        "parallel rail corridor",
        "repeating platform columns",
    ),
)


OLD_STATION_DEFAULT = LocationVariant(
    world_id="studio_world",
    location_id="old_station",
    variant_id="default",
    display_name="Old Railway Station - Default",
    summary=(
        "The canonical neutral presentation of the old station."
    ),
    descriptors=(
        "dry platform surfaces",
        "restrained daylight-neutral ambience",
        "clear architectural silhouette",
        "unobstructed platform circulation",
    ),
)


OLD_STATION_RAINY_NIGHT = LocationVariant(
    world_id="studio_world",
    location_id="old_station",
    variant_id="rainy_night",
    display_name="Old Railway Station - Rainy Night",
    summary=(
        "The same station during a restrained rainy night."
    ),
    descriptors=(
        "wet platform surfaces",
        "cool night atmosphere",
        "warm practical light accents",
        "soft atmospheric depth separation",
    ),
)


STATION_BENCH = PropIdentity(
    world_id="studio_world",
    prop_id="station_bench",
    display_name="Old Station Bench",
    summary=(
        "A persistent simple platform bench used throughout "
        "the old railway station."
    ),
    anchors=(
        "long three-seat silhouette",
        "dark supporting frame",
        "simple horizontal seat and backrest",
    ),
)


STATION_BENCH_DEFAULT = PropVariant(
    world_id="studio_world",
    prop_id="station_bench",
    variant_id="default",
    display_name="Old Station Bench - Default",
    summary=(
        "The canonical production presentation of the station bench."
    ),
    descriptors=(
        "weathered restrained surface",
        "identity silhouette unchanged",
    ),
)


DEFAULT_WORLD_CATALOG = WorldCatalog(
    worlds=(
        STUDIO_WORLD,
    ),
    locations=(
        OLD_STATION,
    ),
    location_variants=(
        OLD_STATION_DEFAULT,
        OLD_STATION_RAINY_NIGHT,
    ),
    props=(
        STATION_BENCH,
    ),
    prop_variants=(
        STATION_BENCH_DEFAULT,
    ),
)
