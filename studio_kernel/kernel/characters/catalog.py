"""Canonical persistent character catalog for Studio."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import (
    CharacterAppearanceIdentity,
    CharacterIdentity,
    CharacterPerformanceIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
)


class CharacterCatalogError(ValueError):
    """Represent an invalid Studio character catalog."""


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterCatalog:
    """Resolve persistent identities and their appearance variants."""

    identities: tuple[
        CharacterIdentity,
        ...,
    ] = field(
        default_factory=tuple
    )

    variants: tuple[
        CharacterVariant,
        ...,
    ] = field(
        default_factory=tuple
    )

    def __post_init__(
        self,
    ) -> None:
        """Validate catalog member types, uniqueness, and references."""

        if not isinstance(
            self.identities,
            tuple,
        ):
            raise CharacterCatalogError(
                "identities must be a tuple."
            )

        if not isinstance(
            self.variants,
            tuple,
        ):
            raise CharacterCatalogError(
                "variants must be a tuple."
            )

        for index, identity in enumerate(
            self.identities
        ):
            if not isinstance(
                identity,
                CharacterIdentity,
            ):
                raise CharacterCatalogError(
                    "identities["
                    + str(index)
                    + "] must be CharacterIdentity."
                )

        for index, variant in enumerate(
            self.variants
        ):
            if not isinstance(
                variant,
                CharacterVariant,
            ):
                raise CharacterCatalogError(
                    "variants["
                    + str(index)
                    + "] must be CharacterVariant."
                )

        identity_ids = tuple(
            identity.character_id
            for identity in self.identities
        )

        if len(
            set(identity_ids)
        ) != len(identity_ids):
            raise CharacterCatalogError(
                "Character catalog contains duplicate character IDs."
            )

        variant_keys = tuple(
            (
                variant.character_id,
                variant.variant_id,
            )
            for variant in self.variants
        )

        if len(
            set(variant_keys)
        ) != len(variant_keys):
            raise CharacterCatalogError(
                "Character catalog contains duplicate character variants."
            )

        known_identity_ids = set(
            identity_ids
        )

        for variant in self.variants:
            if (
                variant.character_id
                not in known_identity_ids
            ):
                raise CharacterCatalogError(
                    "Character variant references unknown character: "
                    + variant.character_id
                )

    def get_identity(
        self,
        character_id: str,
    ) -> CharacterIdentity | None:
        """Return a persistent identity by stable character ID."""

        for identity in self.identities:
            if identity.character_id == character_id:
                return identity

        return None

    def get_variant(
        self,
        character_id: str,
        variant_id: str = "default",
    ) -> CharacterVariant | None:
        """Return one character appearance variant."""

        for variant in self.variants:
            if (
                variant.character_id == character_id
                and variant.variant_id == variant_id
            ):
                return variant

        return None

    def variants_for(
        self,
        character_id: str,
    ) -> tuple[
        CharacterVariant,
        ...,
    ]:
        """Return all variants belonging to one persistent identity."""

        return tuple(
            variant
            for variant in self.variants
            if variant.character_id == character_id
        )


MOMO_IDENTITY = CharacterIdentity(
    character_id="momo",
    display_name="Momo",
    appearance=CharacterAppearanceIdentity(
        summary=(
            "A youthful anime character whose identity remains "
            "recognizable through a clear silhouette, consistent "
            "facial proportions, and stable core color relationships."
        ),
        anchors=(
            "recognizable silhouette",
            "consistent facial proportions",
            "stable core color identity",
        ),
    ),
    performance=CharacterPerformanceIdentity(
        summary=(
            "Observant and warm, with restrained expressive acting "
            "and deliberate movement that reads clearly in key poses."
        ),
        traits=(
            "observant",
            "warm",
            "deliberate movement",
        ),
    ),
)


MOMO_DEFAULT_VARIANT = CharacterVariant(
    character_id="momo",
    variant_id="default",
    display_name="Momo - Default",
    appearance=CharacterVariantAppearance(
        summary=(
            "Momo's baseline appearance used when no "
            "scene-specific variant is requested."
        ),
        descriptors=(
            "default hairstyle",
            "default everyday outfit",
            "default palette relationship",
        ),
    ),
)


DEFAULT_CHARACTER_CATALOG = CharacterCatalog(
    identities=(
        MOMO_IDENTITY,
    ),
    variants=(
        MOMO_DEFAULT_VARIANT,
    ),
)
