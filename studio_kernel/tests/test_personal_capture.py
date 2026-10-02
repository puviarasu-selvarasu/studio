from __future__ import annotations

import pytest

from kernel.characters.personal_capture import (
    PersonalAnimeCaptureProfile,
    PersonalCaptureError,
    compile_personal_character,
    personal_capture_from_json,
    personal_capture_to_json,
)


def _profile(
    *,
    character_id: str = "sample_person",
) -> PersonalAnimeCaptureProfile:
    return PersonalAnimeCaptureProfile(
        profile_id=(
            character_id
            + "_capture_v1"
        ),
        character_id=character_id,
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


def test_capture_is_generic_for_arbitrary_character_ids() -> None:
    first = _profile(
        character_id="alpha"
    )

    second = _profile(
        character_id="beta"
    )

    assert (
        first.character_id
        != second.character_id
    )


def test_capture_compiles_existing_character_identity_contract() -> None:
    profile = _profile()

    identity, variant = (
        compile_personal_character(
            profile
        )
    )

    assert (
        identity.character_id
        == profile.character_id
    )

    assert (
        variant.character_id
        == profile.character_id
    )

    assert (
        variant.variant_id
        == "default"
    )


def test_capture_round_trip() -> None:
    original = _profile()

    restored = (
        personal_capture_from_json(
            personal_capture_to_json(
                original
            )
        )
    )

    assert restored == original


def test_capture_rejects_invalid_enum() -> None:
    with pytest.raises(
        PersonalCaptureError
    ):
        PersonalAnimeCaptureProfile(
            profile_id="bad",
            character_id="bad",
            display_name="Bad",
            face_shape="unknown",
            hair_shape="short",
            hair_texture="straight",
            brow_style="medium",
            eye_shape="almond",
            nose_profile="straight",
            facial_hair_style="none",
            body_silhouette="average",
            skin_color="#80513A",
            hair_color="#111111",
            eye_color="#222222",
            outfit_color="#333333",
            shoulder_scale=1.0,
            torso_scale=1.0,
            head_scale=1.0,
            reference_roles=(
                "front",
                "left",
                "right",
            ),
        )


def test_capture_rejects_bad_color() -> None:
    with pytest.raises(
        PersonalCaptureError
    ):
        PersonalAnimeCaptureProfile(
            profile_id="bad",
            character_id="bad",
            display_name="Bad",
            face_shape="oval",
            hair_shape="short",
            hair_texture="straight",
            brow_style="medium",
            eye_shape="almond",
            nose_profile="straight",
            facial_hair_style="none",
            body_silhouette="average",
            skin_color="brown",
            hair_color="#111111",
            eye_color="#222222",
            outfit_color="#333333",
            shoulder_scale=1.0,
            torso_scale=1.0,
            head_scale=1.0,
            reference_roles=(
                "front",
                "left",
                "right",
            ),
        )


def test_capture_contains_no_photo_or_biometric_storage() -> None:
    profile = _profile()

    assert not hasattr(
        profile,
        "image_bytes",
    )

    assert not hasattr(
        profile,
        "face_embedding",
    )

    assert not hasattr(
        profile,
        "photo_path",
    )
