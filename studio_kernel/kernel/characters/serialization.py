"""Deterministic serialization for Studio character catalogs."""

from __future__ import annotations

import json
from typing import Any

from .catalog import (
    CharacterCatalog,
    CharacterCatalogError,
)
from .models import (
    CharacterAppearanceIdentity,
    CharacterIdentity,
    CharacterIdentityError,
    CharacterPerformanceIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
)


CHARACTER_CATALOG_SCHEMA_VERSION = 1


class CharacterCatalogSerializationError(ValueError):
    """Represent invalid serialized character-catalog data."""


def character_catalog_to_data(
    catalog: CharacterCatalog,
) -> dict[str, object]:
    """Convert a character catalog into versioned primitive data."""

    if not isinstance(
        catalog,
        CharacterCatalog,
    ):
        raise CharacterCatalogSerializationError(
            "catalog must be CharacterCatalog."
        )

    return {
        "schema_version": CHARACTER_CATALOG_SCHEMA_VERSION,
        "identities": [
            {
                "character_id": identity.character_id,
                "display_name": identity.display_name,
                "appearance": {
                    "summary": identity.appearance.summary,
                    "anchors": list(
                        identity.appearance.anchors
                    ),
                },
                "performance": {
                    "summary": identity.performance.summary,
                    "traits": list(
                        identity.performance.traits
                    ),
                },
            }
            for identity in catalog.identities
        ],
        "variants": [
            {
                "character_id": variant.character_id,
                "variant_id": variant.variant_id,
                "display_name": variant.display_name,
                "appearance": {
                    "summary": variant.appearance.summary,
                    "descriptors": list(
                        variant.appearance.descriptors
                    ),
                },
            }
            for variant in catalog.variants
        ],
    }


def character_catalog_to_json(
    catalog: CharacterCatalog,
) -> str:
    """Serialize a catalog to stable human-readable JSON."""

    return json.dumps(
        character_catalog_to_data(
            catalog
        ),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def character_catalog_from_json(
    raw_json: str,
) -> CharacterCatalog:
    """Deserialize versioned JSON into validated domain objects."""

    if not isinstance(
        raw_json,
        str,
    ):
        raise CharacterCatalogSerializationError(
            "Character catalog JSON must be a string."
        )

    if not raw_json.strip():
        raise CharacterCatalogSerializationError(
            "Character catalog JSON must not be empty."
        )

    try:
        data = json.loads(
            raw_json
        )
    except json.JSONDecodeError as exc:
        raise CharacterCatalogSerializationError(
            f"Invalid character catalog JSON: {exc}"
        ) from exc

    return character_catalog_from_data(
        data
    )


def character_catalog_from_data(
    data: object,
) -> CharacterCatalog:
    """Build a validated character catalog from primitive data."""

    root = _require_mapping(
        data,
        label="catalog",
    )

    _require_exact_keys(
        root,
        {
            "schema_version",
            "identities",
            "variants",
        },
        label="catalog",
    )

    version = root[
        "schema_version"
    ]

    if (
        not isinstance(
            version,
            int,
        )
        or isinstance(
            version,
            bool,
        )
    ):
        raise CharacterCatalogSerializationError(
            "schema_version must be an integer."
        )

    if (
        version
        != CHARACTER_CATALOG_SCHEMA_VERSION
    ):
        raise CharacterCatalogSerializationError(
            "Unsupported character catalog schema version: "
            + str(version)
        )

    identities_data = _require_list(
        root["identities"],
        label="identities",
    )

    variants_data = _require_list(
        root["variants"],
        label="variants",
    )

    try:
        identities = tuple(
            _identity_from_data(
                item,
                index=index,
            )
            for index, item in enumerate(
                identities_data
            )
        )

        variants = tuple(
            _variant_from_data(
                item,
                index=index,
            )
            for index, item in enumerate(
                variants_data
            )
        )

        return CharacterCatalog(
            identities=identities,
            variants=variants,
        )

    except (
        CharacterIdentityError,
        CharacterCatalogError,
    ) as exc:
        raise CharacterCatalogSerializationError(
            "Serialized character catalog violates domain rules: "
            + str(exc)
        ) from exc


def _identity_from_data(
    data: object,
    *,
    index: int,
) -> CharacterIdentity:
    mapping = _require_mapping(
        data,
        label=f"identities[{index}]",
    )

    _require_exact_keys(
        mapping,
        {
            "character_id",
            "display_name",
            "appearance",
            "performance",
        },
        label=f"identities[{index}]",
    )

    appearance_data = _require_mapping(
        mapping["appearance"],
        label=(
            f"identities[{index}].appearance"
        ),
    )

    _require_exact_keys(
        appearance_data,
        {
            "summary",
            "anchors",
        },
        label=(
            f"identities[{index}].appearance"
        ),
    )

    performance_data = _require_mapping(
        mapping["performance"],
        label=(
            f"identities[{index}].performance"
        ),
    )

    _require_exact_keys(
        performance_data,
        {
            "summary",
            "traits",
        },
        label=(
            f"identities[{index}].performance"
        ),
    )

    return CharacterIdentity(
        character_id=_require_string(
            mapping["character_id"],
            label=(
                f"identities[{index}].character_id"
            ),
        ),
        display_name=_require_string(
            mapping["display_name"],
            label=(
                f"identities[{index}].display_name"
            ),
        ),
        appearance=CharacterAppearanceIdentity(
            summary=_require_string(
                appearance_data["summary"],
                label=(
                    f"identities[{index}]"
                    ".appearance.summary"
                ),
            ),
            anchors=_require_string_tuple(
                appearance_data["anchors"],
                label=(
                    f"identities[{index}]"
                    ".appearance.anchors"
                ),
            ),
        ),
        performance=CharacterPerformanceIdentity(
            summary=_require_string(
                performance_data["summary"],
                label=(
                    f"identities[{index}]"
                    ".performance.summary"
                ),
            ),
            traits=_require_string_tuple(
                performance_data["traits"],
                label=(
                    f"identities[{index}]"
                    ".performance.traits"
                ),
            ),
        ),
    )


def _variant_from_data(
    data: object,
    *,
    index: int,
) -> CharacterVariant:
    mapping = _require_mapping(
        data,
        label=f"variants[{index}]",
    )

    _require_exact_keys(
        mapping,
        {
            "character_id",
            "variant_id",
            "display_name",
            "appearance",
        },
        label=f"variants[{index}]",
    )

    appearance_data = _require_mapping(
        mapping["appearance"],
        label=(
            f"variants[{index}].appearance"
        ),
    )

    _require_exact_keys(
        appearance_data,
        {
            "summary",
            "descriptors",
        },
        label=(
            f"variants[{index}].appearance"
        ),
    )

    return CharacterVariant(
        character_id=_require_string(
            mapping["character_id"],
            label=(
                f"variants[{index}].character_id"
            ),
        ),
        variant_id=_require_string(
            mapping["variant_id"],
            label=(
                f"variants[{index}].variant_id"
            ),
        ),
        display_name=_require_string(
            mapping["display_name"],
            label=(
                f"variants[{index}].display_name"
            ),
        ),
        appearance=CharacterVariantAppearance(
            summary=_require_string(
                appearance_data["summary"],
                label=(
                    f"variants[{index}]"
                    ".appearance.summary"
                ),
            ),
            descriptors=_require_string_tuple(
                appearance_data["descriptors"],
                label=(
                    f"variants[{index}]"
                    ".appearance.descriptors"
                ),
            ),
        ),
    )


def _require_mapping(
    value: object,
    *,
    label: str,
) -> dict[str, Any]:
    if not isinstance(
        value,
        dict,
    ):
        raise CharacterCatalogSerializationError(
            f"{label} must be an object."
        )

    if not all(
        isinstance(
            key,
            str,
        )
        for key in value
    ):
        raise CharacterCatalogSerializationError(
            f"{label} keys must be strings."
        )

    return value


def _require_list(
    value: object,
    *,
    label: str,
) -> list[object]:
    if not isinstance(
        value,
        list,
    ):
        raise CharacterCatalogSerializationError(
            f"{label} must be an array."
        )

    return value


def _require_string(
    value: object,
    *,
    label: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise CharacterCatalogSerializationError(
            f"{label} must be a string."
        )

    return value


def _require_string_tuple(
    value: object,
    *,
    label: str,
) -> tuple[str, ...]:
    items = _require_list(
        value,
        label=label,
    )

    return tuple(
        _require_string(
            item,
            label=f"{label}[{index}]",
        )
        for index, item in enumerate(
            items
        )
    )


def _require_exact_keys(
    mapping: dict[str, Any],
    expected: set[str],
    *,
    label: str,
) -> None:
    actual = set(
        mapping
    )

    if actual != expected:
        missing = sorted(
            expected - actual
        )

        extra = sorted(
            actual - expected
        )

        details: list[str] = []

        if missing:
            details.append(
                "missing="
                + ",".join(
                    missing
                )
            )

        if extra:
            details.append(
                "extra="
                + ",".join(
                    extra
                )
            )

        raise CharacterCatalogSerializationError(
            f"{label} has invalid fields: "
            + "; ".join(
                details
            )
        )
