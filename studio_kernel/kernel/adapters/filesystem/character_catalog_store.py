"""Filesystem persistence adapter for Studio character catalogs."""

from __future__ import annotations

from pathlib import Path

from kernel.characters.catalog import (
    CharacterCatalog,
)
from kernel.characters.serialization import (
    CharacterCatalogSerializationError,
    character_catalog_from_json,
    character_catalog_to_json,
)


class CharacterCatalogStoreError(Exception):
    """Represent character catalog filesystem persistence failure."""


def save_character_catalog(
    catalog: CharacterCatalog,
    path: Path,
) -> Path:
    """Persist a character catalog atomically as versioned JSON."""

    destination = Path(
        path
    )

    try:
        serialized = character_catalog_to_json(
            catalog
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = destination.with_name(
            destination.name
            + ".tmp"
        )

        temporary.write_text(
            serialized + "\n",
            encoding="utf-8",
            newline="\n",
        )

        temporary.replace(
            destination
        )

    except (
        OSError,
        CharacterCatalogSerializationError,
    ) as exc:
        raise CharacterCatalogStoreError(
            "Unable to save character catalog: "
            + str(exc)
        ) from exc

    return destination


def load_character_catalog(
    path: Path,
) -> CharacterCatalog:
    """Load a persisted character catalog into validated domain objects."""

    source = Path(
        path
    )

    try:
        raw_json = source.read_text(
            encoding="utf-8"
        )

        return character_catalog_from_json(
            raw_json
        )

    except (
        OSError,
        CharacterCatalogSerializationError,
    ) as exc:
        raise CharacterCatalogStoreError(
            "Unable to load character catalog: "
            + str(exc)
        ) from exc
