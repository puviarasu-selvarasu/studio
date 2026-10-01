"""Application service for resolving trusted character production."""

from __future__ import annotations

from kernel.characters import (
    CharacterCatalog,
    CharacterProductionSpec,
    CharacterProductionSpecError,
    DEFAULT_CHARACTER_CATALOG,
    compile_character_production,
)


class CharacterProductionServiceError(ValueError):
    """Represent an invalid application-to-production character handoff."""


class CharacterProductionService:
    """Resolve semantic character selection into trusted production data."""

    def __init__(
        self,
        catalog: CharacterCatalog = DEFAULT_CHARACTER_CATALOG,
    ) -> None:
        """Initialize with an explicit character catalog."""

        if not isinstance(
            catalog,
            CharacterCatalog,
        ):
            raise CharacterProductionServiceError(
                "catalog must be CharacterCatalog."
            )

        self._catalog = catalog

    def compile_selection(
        self,
        *,
        character_id: str,
        variant_id: str = "default",
    ) -> CharacterProductionSpec:
        """Compile one trusted identity + variant selection for production."""

        if (
            not isinstance(
                character_id,
                str,
            )
            or not character_id.strip()
        ):
            raise CharacterProductionServiceError(
                "character_id must not be empty."
            )

        if (
            not isinstance(
                variant_id,
                str,
            )
            or not variant_id.strip()
        ):
            raise CharacterProductionServiceError(
                "variant_id must not be empty."
            )

        character_id = character_id.strip()
        variant_id = variant_id.strip()

        identity = self._catalog.get_identity(
            character_id
        )

        if identity is None:
            raise CharacterProductionServiceError(
                f"Character identity '{character_id}' is not registered."
            )

        variant = self._catalog.get_variant(
            character_id,
            variant_id,
        )

        if variant is None:
            raise CharacterProductionServiceError(
                "Character variant "
                f"'{character_id}:{variant_id}' is not registered."
            )

        try:
            return compile_character_production(
                identity,
                variant,
            )

        except CharacterProductionSpecError as exc:
            raise CharacterProductionServiceError(
                "Character selection cannot enter production: "
                + str(exc)
            ) from exc
