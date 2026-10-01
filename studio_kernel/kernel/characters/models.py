"""Pure domain models for persistent Studio character identity."""

from __future__ import annotations

import re
from dataclasses import dataclass


class CharacterIdentityError(ValueError):
    """Represent an invalid persistent character identity."""


_CHARACTER_ID_PATTERN = re.compile(
    r"^[a-z][a-z0-9_-]*$"
)


def _required_text(
    value: str,
    *,
    label: str,
) -> str:
    """Return normalized non-empty domain text."""

    if not isinstance(
        value,
        str,
    ):
        raise CharacterIdentityError(
            f"{label} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise CharacterIdentityError(
            f"{label} must not be empty."
        )

    return normalized


def _required_unique_texts(
    values: tuple[str, ...],
    *,
    label: str,
) -> tuple[str, ...]:
    """Normalize a required ordered set of identity descriptors."""

    if not isinstance(
        values,
        tuple,
    ):
        raise CharacterIdentityError(
            f"{label} must be a tuple."
        )

    normalized = tuple(
        _required_text(
            value,
            label=f"{label}[{index}]",
        )
        for index, value in enumerate(
            values
        )
    )

    if not normalized:
        raise CharacterIdentityError(
            f"{label} must contain at least one value."
        )

    if len(
        set(normalized)
    ) != len(normalized):
        raise CharacterIdentityError(
            f"{label} must not contain duplicates."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterAppearanceIdentity:
    """Describe appearance traits that remain part of character identity."""

    summary: str
    anchors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Normalize and validate canonical appearance identity."""

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="appearance.summary",
            ),
        )

        object.__setattr__(
            self,
            "anchors",
            _required_unique_texts(
                self.anchors,
                label="appearance.anchors",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterPerformanceIdentity:
    """Describe persistent acting and movement identity."""

    summary: str
    traits: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Normalize and validate canonical performance identity."""

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="performance.summary",
            ),
        )

        object.__setattr__(
            self,
            "traits",
            _required_unique_texts(
                self.traits,
                label="performance.traits",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterIdentity:
    """Describe one stable character independently of production variants."""

    character_id: str
    display_name: str
    appearance: CharacterAppearanceIdentity
    performance: CharacterPerformanceIdentity

    def __post_init__(
        self,
    ) -> None:
        """Validate stable character metadata and nested identity contracts."""

        character_id = _required_text(
            self.character_id,
            label="character_id",
        )

        if _CHARACTER_ID_PATTERN.fullmatch(
            character_id
        ) is None:
            raise CharacterIdentityError(
                "character_id must be a lowercase stable identifier "
                "using letters, numbers, '_' or '-'."
            )

        display_name = _required_text(
            self.display_name,
            label="display_name",
        )

        if not isinstance(
            self.appearance,
            CharacterAppearanceIdentity,
        ):
            raise CharacterIdentityError(
                "appearance must be CharacterAppearanceIdentity."
            )

        if not isinstance(
            self.performance,
            CharacterPerformanceIdentity,
        ):
            raise CharacterIdentityError(
                "performance must be CharacterPerformanceIdentity."
            )

        object.__setattr__(
            self,
            "character_id",
            character_id,
        )

        object.__setattr__(
            self,
            "display_name",
            display_name,
        )

@dataclass(
    frozen=True,
    slots=True,
)
class CharacterVariantAppearance:
    """Describe appearance details that may change between variants."""

    summary: str
    descriptors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Normalize and validate variant-specific appearance."""

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="variant.appearance.summary",
            ),
        )

        object.__setattr__(
            self,
            "descriptors",
            _required_unique_texts(
                self.descriptors,
                label="variant.appearance.descriptors",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterVariant:
    """Describe one appearance variant of a persistent character."""

    character_id: str
    variant_id: str
    display_name: str
    appearance: CharacterVariantAppearance

    def __post_init__(
        self,
    ) -> None:
        """Validate stable identity reference and variant metadata."""

        character_id = _required_text(
            self.character_id,
            label="character_id",
        )

        if _CHARACTER_ID_PATTERN.fullmatch(
            character_id
        ) is None:
            raise CharacterIdentityError(
                "character_id must be a lowercase stable identifier "
                "using letters, numbers, '_' or '-'."
            )

        variant_id = _required_text(
            self.variant_id,
            label="variant_id",
        )

        if _CHARACTER_ID_PATTERN.fullmatch(
            variant_id
        ) is None:
            raise CharacterIdentityError(
                "variant_id must be a lowercase stable identifier "
                "using letters, numbers, '_' or '-'."
            )

        display_name = _required_text(
            self.display_name,
            label="variant.display_name",
        )

        if not isinstance(
            self.appearance,
            CharacterVariantAppearance,
        ):
            raise CharacterIdentityError(
                "variant appearance must be "
                "CharacterVariantAppearance."
            )

        object.__setattr__(
            self,
            "character_id",
            character_id,
        )

        object.__setattr__(
            self,
            "variant_id",
            variant_id,
        )

        object.__setattr__(
            self,
            "display_name",
            display_name,
        )
