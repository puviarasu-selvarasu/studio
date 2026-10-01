"""Character identity domain contracts for Studio."""

from .catalog import (
    CharacterCatalog,
    CharacterCatalogError,
    DEFAULT_CHARACTER_CATALOG,
    MOMO_DEFAULT_VARIANT,
    MOMO_IDENTITY,
)
from .models import (
    CharacterAppearanceIdentity,
    CharacterIdentity,
    CharacterIdentityError,
    CharacterPerformanceIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
)
from .serialization import (
    CHARACTER_CATALOG_SCHEMA_VERSION,
    CharacterCatalogSerializationError,
    character_catalog_from_data,
    character_catalog_from_json,
    character_catalog_to_data,
    character_catalog_to_json,
)

__all__ = [
    "CharacterAppearanceIdentity",
    "CharacterCatalog",
    "CharacterCatalogError",
    "CharacterIdentity",
    "CharacterIdentityError",
    "CharacterPerformanceIdentity",
    "CharacterVariant",
    "CharacterVariantAppearance",
    "CHARACTER_CATALOG_SCHEMA_VERSION",
    "CharacterCatalogSerializationError",
    "character_catalog_from_data",
    "character_catalog_from_json",
    "character_catalog_to_data",
    "character_catalog_to_json",
    "DEFAULT_CHARACTER_CATALOG",
    "MOMO_DEFAULT_VARIANT",
    "MOMO_IDENTITY",
]
