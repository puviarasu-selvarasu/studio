"""Tests for Studio's deterministic character-production compiler."""

from __future__ import annotations

from dataclasses import (
    FrozenInstanceError,
    fields,
)
from pathlib import Path

import pytest

from kernel.characters import (
    MOMO_DEFAULT_VARIANT,
    MOMO_IDENTITY,
    CharacterIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
)
from kernel.characters.production import (
    BodyProfile,
    CharacterPaletteProfile,
    CharacterProductionSpec,
    CharacterProductionSpecError,
    CharacterProportions,
    HairProfile,
    OutfitProfile,
    RigProfile,
    compile_character_production,
)


PRODUCTION_SOURCE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "kernel"
    / "characters"
    / "production.py"
)


def test_compile_momo_default_production_spec() -> None:
    spec = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    assert spec.character_id == "momo"
    assert spec.variant_id == "default"

    assert (
        spec.production_profile_id
        == "momo_default_v1"
    )

    assert (
        spec.rig_profile
        is RigProfile.STUDIO_HUMANOID_V1
    )

    assert (
        spec.body_profile
        is BodyProfile.LIGHTWEIGHT_ANIME_V1
    )

    assert (
        spec.hair_profile
        is HairProfile.SHOULDER_LENGTH_DARK_V1
    )

    assert (
        spec.outfit_profile
        is OutfitProfile.SIMPLE_EVERYDAY_V1
    )

    assert (
        spec.palette_profile
        is CharacterPaletteProfile.MOMO_DEFAULT_V1
    )


def test_momo_default_proportions_are_bounded_and_character_specific() -> None:
    spec = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    assert spec.proportions == CharacterProportions(
        head_scale=1.10,
        shoulder_scale=0.92,
        torso_scale=0.92,
        hip_scale=0.90,
        limb_scale=0.88,
    )


def test_compiler_is_deterministic() -> None:
    first = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    second = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    assert first == second
    assert first is not second


def test_production_contract_is_immutable() -> None:
    spec = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        spec.character_id = "changed"


def test_compiler_rejects_variant_from_different_identity() -> None:
    other_identity = CharacterIdentity(
        character_id="akira",
        display_name="Akira",
        appearance=MOMO_IDENTITY.appearance,
        performance=MOMO_IDENTITY.performance,
    )

    with pytest.raises(
        CharacterProductionSpecError,
        match="does not belong",
    ):
        compile_character_production(
            other_identity,
            MOMO_DEFAULT_VARIANT,
        )


def test_compiler_rejects_unregistered_production_variant() -> None:
    winter = CharacterVariant(
        character_id="momo",
        variant_id="winter",
        display_name="Momo - Winter",
        appearance=CharacterVariantAppearance(
            summary="Momo winter appearance.",
            descriptors=(
                "winter coat",
            ),
        ),
    )

    with pytest.raises(
        CharacterProductionSpecError,
        match="No production profile registered",
    ):
        compile_character_production(
            MOMO_IDENTITY,
            winter,
        )


@pytest.mark.parametrize(
    "value",
    (
        0.49,
        1.51,
        True,
        "1.0",
    ),
)
def test_character_proportions_reject_invalid_scales(
    value,
) -> None:
    with pytest.raises(
        CharacterProductionSpecError
    ):
        CharacterProportions(
            head_scale=value,
            shoulder_scale=1.0,
            torso_scale=1.0,
            hip_scale=1.0,
            limb_scale=1.0,
        )


def test_production_spec_contains_no_blender_asset_paths() -> None:
    names = {
        field.name
        for field in fields(
            CharacterProductionSpec
        )
    }

    forbidden_fields = {
        "mesh_path",
        "rig_path",
        "blend_path",
        "texture_path",
        "armature_name",
        "object_name",
        "python_code",
    }

    assert names.isdisjoint(
        forbidden_fields
    )


def test_production_compiler_is_pure_python_and_adapter_independent() -> None:
    source = PRODUCTION_SOURCE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "import bpy",
        "from bpy",
        "kernel.adapters.blender",
        "Ollama",
        "Pydantic",
        "mesh_path",
        "rig_path",
        "blend_path",
        "texture_path",
        "eval(",
        "exec(",
        "Path(",
        ".read_text(",
        ".write_text(",
    )

    for token in forbidden:
        assert token not in source


def test_character_production_json_round_trip() -> None:
    from kernel.characters.production import (
        CHARACTER_PRODUCTION_SCHEMA_VERSION,
        character_production_from_json,
        character_production_to_json,
    )

    spec = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    raw_json = character_production_to_json(
        spec
    )

    restored = character_production_from_json(
        raw_json
    )

    assert restored == spec
    assert CHARACTER_PRODUCTION_SCHEMA_VERSION == 1


def test_character_production_json_is_deterministic() -> None:
    from kernel.characters.production import (
        character_production_to_json,
    )

    spec = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    assert (
        character_production_to_json(
            spec
        )
        == character_production_to_json(
            spec
        )
    )


def test_character_production_json_rejects_extra_fields() -> None:
    import json

    from kernel.characters.production import (
        CharacterProductionSpecError,
        character_production_from_json,
        character_production_to_json,
    )

    spec = compile_character_production(
        MOMO_IDENTITY,
        MOMO_DEFAULT_VARIANT,
    )

    data = json.loads(
        character_production_to_json(
            spec
        )
    )

    data["unsafe_extra"] = "rejected"

    with pytest.raises(
        CharacterProductionSpecError,
        match="invalid fields",
    ):
        character_production_from_json(
            json.dumps(
                data
            )
        )
