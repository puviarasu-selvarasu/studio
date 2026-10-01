"""Tests for application-to-character-production handoff."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.application.character_production_service import (
    CharacterProductionService,
    CharacterProductionServiceError,
)
from kernel.characters import (
    CharacterCatalog,
    CharacterVariant,
    CharacterVariantAppearance,
    MOMO_DEFAULT_VARIANT,
    MOMO_IDENTITY,
)


SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "application"
    / "character_production_service.py"
)


def test_service_compiles_momo_default_selection() -> None:
    service = CharacterProductionService()

    spec = service.compile_selection(
        character_id="momo",
        variant_id="default",
    )

    assert spec.character_id == "momo"
    assert spec.variant_id == "default"
    assert (
        spec.production_profile_id
        == "momo_default_v1"
    )


def test_service_default_variant_is_backward_compatible() -> None:
    service = CharacterProductionService()

    spec = service.compile_selection(
        character_id="momo",
    )

    assert spec.variant_id == "default"


def test_service_rejects_unknown_identity() -> None:
    service = CharacterProductionService()

    with pytest.raises(
        CharacterProductionServiceError,
        match="identity.*not registered",
    ):
        service.compile_selection(
            character_id="unknown",
        )


def test_service_rejects_unknown_variant() -> None:
    service = CharacterProductionService()

    with pytest.raises(
        CharacterProductionServiceError,
        match="variant.*not registered",
    ):
        service.compile_selection(
            character_id="momo",
            variant_id="unknown",
        )


def test_semantic_variant_without_production_profile_stops_at_handoff() -> None:
    winter = CharacterVariant(
        character_id="momo",
        variant_id="winter",
        display_name="Momo - Winter",
        appearance=CharacterVariantAppearance(
            summary="Momo wearing her winter appearance.",
            descriptors=(
                "winter coat",
                "winter scarf",
            ),
        ),
    )

    catalog = CharacterCatalog(
        identities=(
            MOMO_IDENTITY,
        ),
        variants=(
            MOMO_DEFAULT_VARIANT,
            winter,
        ),
    )

    service = CharacterProductionService(
        catalog
    )

    with pytest.raises(
        CharacterProductionServiceError,
        match="cannot enter production",
    ):
        service.compile_selection(
            character_id="momo",
            variant_id="winter",
        )


def test_application_service_has_no_blender_or_ai_dependency() -> None:
    source = SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "import bpy",
        "from bpy",
        "kernel.adapters.blender",
        "BlenderAdapter",
        "Ollama",
        "subprocess",
        "eval(",
        "exec(",
    )

    for token in forbidden:
        assert token not in source
