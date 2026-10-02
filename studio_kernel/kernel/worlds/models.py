"""Pure semantic identity contracts for Studio worlds, locations, and props."""

from __future__ import annotations

import re
from dataclasses import dataclass


class WorldIdentityError(ValueError):
    """Represent invalid semantic world identity data."""


_STABLE_ID = re.compile(
    r"^[a-z][a-z0-9_-]*$"
)


def _stable_id(
    value: str,
    *,
    label: str,
) -> str:
    """Normalize and validate one stable semantic identifier."""

    if not isinstance(
        value,
        str,
    ):
        raise WorldIdentityError(
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
        raise WorldIdentityError(
            f"{label} must be a stable lowercase identifier."
        )

    return normalized


def _required_text(
    value: str,
    *,
    label: str,
) -> str:
    """Normalize one required human-readable semantic value."""

    if not isinstance(
        value,
        str,
    ):
        raise WorldIdentityError(
            f"{label} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise WorldIdentityError(
            f"{label} must not be empty."
        )

    return normalized


def _required_unique_texts(
    values: tuple[str, ...],
    *,
    label: str,
) -> tuple[str, ...]:
    """Validate a non-empty tuple of unique semantic descriptors."""

    if not isinstance(
        values,
        tuple,
    ):
        raise WorldIdentityError(
            f"{label} must be a tuple."
        )

    if not values:
        raise WorldIdentityError(
            f"{label} must not be empty."
        )

    normalized = tuple(
        _required_text(
            value,
            label=(
                f"{label}[{index}]"
            ),
        )
        for index, value
        in enumerate(
            values
        )
    )

    if (
        len(
            set(
                normalized
            )
        )
        != len(
            normalized
        )
    ):
        raise WorldIdentityError(
            f"{label} must contain unique values."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class WorldIdentity:
    """Persistent semantic identity of one fictional world or setting."""

    world_id: str
    display_name: str
    summary: str
    anchors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Validate stable world identity."""

        object.__setattr__(
            self,
            "world_id",
            _stable_id(
                self.world_id,
                label="world_id",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            _required_text(
                self.display_name,
                label="display_name",
            ),
        )

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="summary",
            ),
        )

        object.__setattr__(
            self,
            "anchors",
            _required_unique_texts(
                self.anchors,
                label="anchors",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LocationIdentity:
    """Persistent semantic identity of one reusable place inside a world."""

    world_id: str
    location_id: str
    display_name: str
    summary: str
    anchors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Validate stable location identity."""

        object.__setattr__(
            self,
            "world_id",
            _stable_id(
                self.world_id,
                label="world_id",
            ),
        )

        object.__setattr__(
            self,
            "location_id",
            _stable_id(
                self.location_id,
                label="location_id",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            _required_text(
                self.display_name,
                label="display_name",
            ),
        )

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="summary",
            ),
        )

        object.__setattr__(
            self,
            "anchors",
            _required_unique_texts(
                self.anchors,
                label="anchors",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LocationVariant:
    """Contextual presentation of a location without changing its identity."""

    world_id: str
    location_id: str
    variant_id: str
    display_name: str
    summary: str
    descriptors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Validate a semantic location variant."""

        object.__setattr__(
            self,
            "world_id",
            _stable_id(
                self.world_id,
                label="world_id",
            ),
        )

        object.__setattr__(
            self,
            "location_id",
            _stable_id(
                self.location_id,
                label="location_id",
            ),
        )

        object.__setattr__(
            self,
            "variant_id",
            _stable_id(
                self.variant_id,
                label="variant_id",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            _required_text(
                self.display_name,
                label="display_name",
            ),
        )

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="summary",
            ),
        )

        object.__setattr__(
            self,
            "descriptors",
            _required_unique_texts(
                self.descriptors,
                label="descriptors",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PropIdentity:
    """Persistent semantic identity of one reusable story prop."""

    world_id: str
    prop_id: str
    display_name: str
    summary: str
    anchors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Validate stable prop identity."""

        object.__setattr__(
            self,
            "world_id",
            _stable_id(
                self.world_id,
                label="world_id",
            ),
        )

        object.__setattr__(
            self,
            "prop_id",
            _stable_id(
                self.prop_id,
                label="prop_id",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            _required_text(
                self.display_name,
                label="display_name",
            ),
        )

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="summary",
            ),
        )

        object.__setattr__(
            self,
            "anchors",
            _required_unique_texts(
                self.anchors,
                label="anchors",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class PropVariant:
    """Contextual presentation of a prop without changing its identity."""

    world_id: str
    prop_id: str
    variant_id: str
    display_name: str
    summary: str
    descriptors: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        """Validate a semantic prop variant."""

        object.__setattr__(
            self,
            "world_id",
            _stable_id(
                self.world_id,
                label="world_id",
            ),
        )

        object.__setattr__(
            self,
            "prop_id",
            _stable_id(
                self.prop_id,
                label="prop_id",
            ),
        )

        object.__setattr__(
            self,
            "variant_id",
            _stable_id(
                self.variant_id,
                label="variant_id",
            ),
        )

        object.__setattr__(
            self,
            "display_name",
            _required_text(
                self.display_name,
                label="display_name",
            ),
        )

        object.__setattr__(
            self,
            "summary",
            _required_text(
                self.summary,
                label="summary",
            ),
        )

        object.__setattr__(
            self,
            "descriptors",
            _required_unique_texts(
                self.descriptors,
                label="descriptors",
            ),
        )
