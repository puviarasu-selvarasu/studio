from __future__ import annotations

from pathlib import Path

import pytest

from kernel.characters.anime_2d_design import (
    ART_MODE,
    STYLE_ID,
    Anime2DCharacterDesign,
    Anime2DDesignError,
    Anime2DInkSpec,
    Anime2DViewSpec,
    anime_2d_design_from_json,
    anime_2d_design_to_data,
    anime_2d_design_to_json,
    compile_anime_2d_design,
)
from kernel.characters.personal_capture import PersonalAnimeCaptureProfile


def _profile() -> PersonalAnimeCaptureProfile:
    return PersonalAnimeCaptureProfile(
        profile_id="sample_capture_v1",
        character_id="sample_person",
        display_name="Sample Person",
        face_shape="tapered_oval",
        hair_shape="high_volume",
        hair_texture="wavy",
        brow_style="thick",
        eye_shape="almond",
        nose_profile="prominent",
        facial_hair_style="full_beard",
        body_silhouette="athletic",
        skin_color="#80513A",
        hair_color="#151218",
        eye_color="#321D14",
        outfit_color="#182536",
        shoulder_scale=1.12,
        torso_scale=1.05,
        head_scale=0.98,
        reference_roles=(
            "front",
            "left_profile",
            "right_profile",
            "full_body",
        ),
    )


def test_compile_preserves_phase14_identity_anchors() -> None:
    design = compile_anime_2d_design(_profile())
    assert design.character_id == "sample_person"
    assert design.face_shape == "tapered_oval"
    assert design.hair_shape == "high_volume"
    assert design.hair_texture == "wavy"
    assert design.brow_style == "thick"
    assert design.eye_shape == "almond"
    assert design.nose_profile == "prominent"
    assert design.facial_hair_style == "full_beard"
    assert design.body_silhouette == "athletic"


def test_design_is_explicitly_pure_2d_and_style_locked() -> None:
    design = compile_anime_2d_design(_profile())
    assert design.art_mode == ART_MODE == "pure_2d"
    assert design.style_id == STYLE_ID


def test_acceptance_sheet_contract_is_front_three_quarter_and_expression() -> None:
    design = compile_anime_2d_design(_profile())
    assert tuple((item.view, item.expression) for item in design.acceptance_views) == (
        ("front", "neutral"),
        ("three_quarter_right", "neutral"),
        ("three_quarter_left", "determined"),
    )


def test_ink_contract_requires_visible_width_hierarchy() -> None:
    design = compile_anime_2d_design(_profile())
    assert design.ink.outer_width > design.ink.feature_width > design.ink.detail_width
    with pytest.raises(Anime2DDesignError):
        Anime2DInkSpec(
            outer_width=0.020,
            feature_width=0.030,
            detail_width=0.010,
        )


def test_cel_contract_stays_in_limited_shadow_range() -> None:
    design = compile_anime_2d_design(_profile())
    assert 1 <= design.cel.shadow_layers <= 3
    assert design.cel.hard_edges is True


def test_compile_is_deterministic_for_same_identity() -> None:
    assert compile_anime_2d_design(_profile()) == compile_anime_2d_design(_profile())


def test_serialization_round_trip_is_stable() -> None:
    design = compile_anime_2d_design(_profile())
    encoded = anime_2d_design_to_json(design)
    restored = anime_2d_design_from_json(encoded)
    assert restored == design
    assert anime_2d_design_to_json(restored) == encoded


def test_art_contract_does_not_store_reference_roles_or_photo_paths() -> None:
    data = anime_2d_design_to_data(compile_anime_2d_design(_profile()))
    text = str(data).lower()
    assert "reference_roles" not in text
    assert "photo" not in text
    assert "image_path" not in text


def test_view_contract_rejects_unsupported_values() -> None:
    with pytest.raises(Anime2DDesignError):
        Anime2DViewSpec(
            view="camera_spin",
            expression="neutral",
        )


def test_invalid_serialized_art_mode_is_rejected() -> None:
    design = compile_anime_2d_design(_profile())
    data = anime_2d_design_to_data(design)
    data["art_mode"] = "other"
    import json
    with pytest.raises(Anime2DDesignError):
        anime_2d_design_from_json(json.dumps(data))


def test_domain_contract_has_no_blender_dependency() -> None:
    source_path = (
        Path(__file__).parents[1]
        / "kernel"
        / "characters"
        / "anime_2d_design.py"
    )
    source = source_path.read_text(encoding="utf-8").lower()
    assert "import bpy" not in source
    assert "kernel.adapters.blender" not in source


def test_character_design_is_immutable() -> None:
    design = compile_anime_2d_design(_profile())
    with pytest.raises((AttributeError, TypeError)):
        setattr(design, "character_id", "changed")
    assert isinstance(design, Anime2DCharacterDesign)
