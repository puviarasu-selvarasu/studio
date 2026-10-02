"""Generic reference-driven character capture.

Reference photographs are source material. Persistent Studio identities
store bounded artistic parameters rather than raw photographs or biometric
embeddings. The same profile format is used for every person.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from kernel.characters.models import (
    CharacterAppearanceIdentity,
    CharacterIdentity,
    CharacterPerformanceIdentity,
    CharacterVariant,
    CharacterVariantAppearance,
)


class PersonalCaptureError(ValueError):
    """Raised when generic character-capture data is invalid."""


FACE_SHAPES = frozenset(
    {
        "oval",
        "tapered_oval",
        "round",
        "square",
        "heart",
        "long",
    }
)

HAIR_SHAPES = frozenset(
    {
        "cropped",
        "short",
        "medium",
        "high_volume",
        "swept",
    }
)

HAIR_TEXTURES = frozenset(
    {
        "straight",
        "wavy",
        "curly",
        "coily",
    }
)

BROW_STYLES = frozenset(
    {
        "thin",
        "medium",
        "thick",
    }
)

EYE_SHAPES = frozenset(
    {
        "almond",
        "round",
        "narrow",
    }
)

NOSE_PROFILES = frozenset(
    {
        "soft",
        "straight",
        "prominent",
        "convex",
    }
)

FACIAL_HAIR_STYLES = frozenset(
    {
        "none",
        "moustache",
        "short_beard",
        "full_beard",
    }
)

BODY_SILHOUETTES = frozenset(
    {
        "slim",
        "average",
        "athletic",
        "broad",
    }
)


_HEX = re.compile(
    r"^#[0-9A-Fa-f]{6}$"
)


def _required_text(
    value: str,
    field: str,
) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise PersonalCaptureError(
            field
            + " must not be blank."
        )

    return value.strip()


def _choice(
    value: str,
    allowed: frozenset[str],
    field: str,
) -> str:
    normalized = _required_text(
        value,
        field,
    )

    if normalized not in allowed:
        raise PersonalCaptureError(
            field
            + " contains an unsupported value."
        )

    return normalized


def _scale(
    value: float,
    field: str,
    minimum: float,
    maximum: float,
) -> float:
    number = float(value)

    if not minimum <= number <= maximum:
        raise PersonalCaptureError(
            field
            + " must be between "
            + str(minimum)
            + " and "
            + str(maximum)
            + "."
        )

    return number


def _hex_color(
    value: str,
    field: str,
) -> str:
    normalized = _required_text(
        value,
        field,
    ).upper()

    if _HEX.fullmatch(
        normalized
    ) is None:
        raise PersonalCaptureError(
            field
            + " must use #RRGGBB."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class PersonalAnimeCaptureProfile:
    profile_id: str
    character_id: str
    display_name: str

    face_shape: str

    hair_shape: str
    hair_texture: str

    brow_style: str
    eye_shape: str
    nose_profile: str

    facial_hair_style: str
    body_silhouette: str

    skin_color: str
    hair_color: str
    eye_color: str
    outfit_color: str

    shoulder_scale: float
    torso_scale: float
    head_scale: float

    reference_roles: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        for field in (
            "profile_id",
            "character_id",
            "display_name",
        ):
            object.__setattr__(
                self,
                field,
                _required_text(
                    getattr(
                        self,
                        field,
                    ),
                    field,
                ),
            )

        selections = (
            (
                "face_shape",
                FACE_SHAPES,
            ),
            (
                "hair_shape",
                HAIR_SHAPES,
            ),
            (
                "hair_texture",
                HAIR_TEXTURES,
            ),
            (
                "brow_style",
                BROW_STYLES,
            ),
            (
                "eye_shape",
                EYE_SHAPES,
            ),
            (
                "nose_profile",
                NOSE_PROFILES,
            ),
            (
                "facial_hair_style",
                FACIAL_HAIR_STYLES,
            ),
            (
                "body_silhouette",
                BODY_SILHOUETTES,
            ),
        )

        for field, allowed in selections:
            object.__setattr__(
                self,
                field,
                _choice(
                    getattr(
                        self,
                        field,
                    ),
                    allowed,
                    field,
                ),
            )

        for field in (
            "skin_color",
            "hair_color",
            "eye_color",
            "outfit_color",
        ):
            object.__setattr__(
                self,
                field,
                _hex_color(
                    getattr(
                        self,
                        field,
                    ),
                    field,
                ),
            )

        object.__setattr__(
            self,
            "shoulder_scale",
            _scale(
                self.shoulder_scale,
                "shoulder_scale",
                0.80,
                1.30,
            ),
        )

        object.__setattr__(
            self,
            "torso_scale",
            _scale(
                self.torso_scale,
                "torso_scale",
                0.80,
                1.25,
            ),
        )

        object.__setattr__(
            self,
            "head_scale",
            _scale(
                self.head_scale,
                "head_scale",
                0.85,
                1.15,
            ),
        )

        if (
            not isinstance(
                self.reference_roles,
                tuple,
            )
            or len(
                self.reference_roles
            )
            < 3
        ):
            raise PersonalCaptureError(
                "At least three reference roles are required."
            )

        normalized = tuple(
            _required_text(
                role,
                "reference role",
            )
            for role
            in self.reference_roles
        )

        if (
            len(normalized)
            != len(set(normalized))
        ):
            raise PersonalCaptureError(
                "Reference roles must be unique."
            )

        object.__setattr__(
            self,
            "reference_roles",
            normalized,
        )


def compile_personal_character(
    profile: PersonalAnimeCaptureProfile,
) -> tuple[
    CharacterIdentity,
    CharacterVariant,
]:
    """Compile capture data into Studio's existing semantic identity model."""

    anchors = (
        (
            profile.hair_shape
            + " "
            + profile.hair_texture
            + " hair"
        ),
        (
            profile.brow_style
            + " brows"
        ),
        (
            profile.eye_shape
            + " eyes"
        ),
        (
            profile.nose_profile
            + " nose profile"
        ),
        (
            profile.facial_hair_style
            + " facial hair"
        ),
        (
            profile.face_shape
            + " facial silhouette"
        ),
        (
            profile.body_silhouette
            + " body silhouette"
        ),
    )

    identity = CharacterIdentity(
        character_id=(
            profile.character_id
        ),
        display_name=(
            profile.display_name
        ),
        appearance=(
            CharacterAppearanceIdentity(
                summary=(
                    "Reference-derived personal anime "
                    "identity using bounded artistic cues."
                ),
                anchors=anchors,
            )
        ),
        performance=(
            CharacterPerformanceIdentity(
                summary=(
                    "Performance remains independent "
                    "from captured appearance."
                ),
                traits=(
                    "reference-derived",
                    "director-controlled",
                ),
            )
        ),
    )

    variant = CharacterVariant(
        character_id=(
            profile.character_id
        ),
        variant_id="default",
        display_name=(
            "Default Anime"
        ),
        appearance=(
            CharacterVariantAppearance(
                summary=(
                    "Default anime presentation of "
                    "the captured personal identity."
                ),
                descriptors=(
                    profile.face_shape,
                    profile.hair_shape,
                    profile.hair_texture,
                    profile.brow_style,
                    profile.eye_shape,
                    profile.nose_profile,
                    profile.facial_hair_style,
                    profile.body_silhouette,
                ),
            )
        ),
    )

    return (
        identity,
        variant,
    )


def personal_capture_to_data(
    profile: PersonalAnimeCaptureProfile,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "profile_id": profile.profile_id,
        "character_id": profile.character_id,
        "display_name": profile.display_name,
        "face_shape": profile.face_shape,
        "hair_shape": profile.hair_shape,
        "hair_texture": profile.hair_texture,
        "brow_style": profile.brow_style,
        "eye_shape": profile.eye_shape,
        "nose_profile": profile.nose_profile,
        "facial_hair_style": profile.facial_hair_style,
        "body_silhouette": profile.body_silhouette,
        "skin_color": profile.skin_color,
        "hair_color": profile.hair_color,
        "eye_color": profile.eye_color,
        "outfit_color": profile.outfit_color,
        "shoulder_scale": profile.shoulder_scale,
        "torso_scale": profile.torso_scale,
        "head_scale": profile.head_scale,
        "reference_roles": list(
            profile.reference_roles
        ),
    }


def personal_capture_to_json(
    profile: PersonalAnimeCaptureProfile,
) -> str:
    return (
        json.dumps(
            personal_capture_to_data(
                profile
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def personal_capture_from_data(
    data: dict[str, object],
) -> PersonalAnimeCaptureProfile:
    expected = {
        "schema_version",
        "profile_id",
        "character_id",
        "display_name",
        "face_shape",
        "hair_shape",
        "hair_texture",
        "brow_style",
        "eye_shape",
        "nose_profile",
        "facial_hair_style",
        "body_silhouette",
        "skin_color",
        "hair_color",
        "eye_color",
        "outfit_color",
        "shoulder_scale",
        "torso_scale",
        "head_scale",
        "reference_roles",
    }

    if set(data) != expected:
        raise PersonalCaptureError(
            "Capture profile keys are invalid."
        )

    if data[
        "schema_version"
    ] != 1:
        raise PersonalCaptureError(
            "Unsupported capture profile schema."
        )

    roles = data[
        "reference_roles"
    ]

    if not isinstance(
        roles,
        list,
    ):
        raise PersonalCaptureError(
            "reference_roles must be a list."
        )

    return PersonalAnimeCaptureProfile(
        profile_id=str(
            data[
                "profile_id"
            ]
        ),
        character_id=str(
            data[
                "character_id"
            ]
        ),
        display_name=str(
            data[
                "display_name"
            ]
        ),
        face_shape=str(
            data[
                "face_shape"
            ]
        ),
        hair_shape=str(
            data[
                "hair_shape"
            ]
        ),
        hair_texture=str(
            data[
                "hair_texture"
            ]
        ),
        brow_style=str(
            data[
                "brow_style"
            ]
        ),
        eye_shape=str(
            data[
                "eye_shape"
            ]
        ),
        nose_profile=str(
            data[
                "nose_profile"
            ]
        ),
        facial_hair_style=str(
            data[
                "facial_hair_style"
            ]
        ),
        body_silhouette=str(
            data[
                "body_silhouette"
            ]
        ),
        skin_color=str(
            data[
                "skin_color"
            ]
        ),
        hair_color=str(
            data[
                "hair_color"
            ]
        ),
        eye_color=str(
            data[
                "eye_color"
            ]
        ),
        outfit_color=str(
            data[
                "outfit_color"
            ]
        ),
        shoulder_scale=float(
            data[
                "shoulder_scale"
            ]
        ),
        torso_scale=float(
            data[
                "torso_scale"
            ]
        ),
        head_scale=float(
            data[
                "head_scale"
            ]
        ),
        reference_roles=tuple(
            str(item)
            for item
            in roles
        ),
    )


def personal_capture_from_json(
    raw: str,
) -> PersonalAnimeCaptureProfile:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PersonalCaptureError(
            "Capture profile is not valid JSON."
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise PersonalCaptureError(
            "Capture profile must be an object."
        )

    return personal_capture_from_data(
        data
    )
