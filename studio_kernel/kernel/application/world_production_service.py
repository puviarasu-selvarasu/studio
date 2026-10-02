"""Application handoff from semantic world selection to production spec."""

from __future__ import annotations

from kernel.worlds import (
    DEFAULT_WORLD_CATALOG,
    WorldCatalog,
    WorldProductionSpec,
    compile_world_production,
)


class WorldProductionServiceError(ValueError):
    """Represent an invalid world-production application selection."""


class WorldProductionService:
    """Resolve catalog selections and compile bounded world production."""

    def __init__(
        self,
        catalog: WorldCatalog = DEFAULT_WORLD_CATALOG,
    ) -> None:
        if not isinstance(
            catalog,
            WorldCatalog,
        ):
            raise WorldProductionServiceError(
                "catalog must be WorldCatalog."
            )

        self._catalog = catalog

    def compile_selection(
        self,
        world_id: str,
        location_id: str,
        variant_id: str = "default",
        *,
        prop_selections: tuple[
            tuple[
                str,
                str,
            ],
            ...,
        ] = (),
    ) -> WorldProductionSpec:
        """Resolve semantic IDs and compile one trusted production handoff."""

        world = self._catalog.get_world(
            world_id
        )

        if world is None:
            raise WorldProductionServiceError(
                "Unknown world_id: "
                + str(
                    world_id
                )
            )

        location = self._catalog.get_location(
            world_id,
            location_id,
        )

        if location is None:
            raise WorldProductionServiceError(
                "Unknown location_id for world: "
                + str(
                    location_id
                )
            )

        variant = (
            self._catalog.get_location_variant(
                world_id,
                location_id,
                variant_id,
            )
        )

        if variant is None:
            raise WorldProductionServiceError(
                "Unknown location variant: "
                + str(
                    variant_id
                )
            )

        if not isinstance(
            prop_selections,
            tuple,
        ):
            raise WorldProductionServiceError(
                "prop_selections must be a tuple."
            )

        resolved_props = []

        for selection in prop_selections:
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
                raise WorldProductionServiceError(
                    "Each prop selection must be "
                    "(prop_id, variant_id)."
                )

            prop_id, prop_variant_id = (
                selection
            )

            prop = self._catalog.get_prop(
                world_id,
                prop_id,
            )

            if prop is None:
                raise WorldProductionServiceError(
                    "Unknown prop_id for world: "
                    + str(
                        prop_id
                    )
                )

            prop_variant = (
                self._catalog.get_prop_variant(
                    world_id,
                    prop_id,
                    prop_variant_id,
                )
            )

            if prop_variant is None:
                raise WorldProductionServiceError(
                    "Unknown prop variant: "
                    + str(
                        prop_variant_id
                    )
                )

            resolved_props.append(
                (
                    prop,
                    prop_variant,
                )
            )

        return compile_world_production(
            world,
            location,
            variant,
            props=tuple(
                resolved_props
            ),
        )
