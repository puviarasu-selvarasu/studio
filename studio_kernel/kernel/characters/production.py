"""Pure character-production specification and deterministic compiler."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum

from .models import (
    CharacterIdentity,
    CharacterVariant,
)


class CharacterProductionSpecError(ValueError):
    """Represent an invalid or unsupported character production specification."""


class RigProfile(str, Enum):
    """Bounded rig families understood by trusted production adapters."""

    STUDIO_HUMANOID_V1 = "studio_humanoid_v1"


class BodyProfile(str, Enum):
    """Bounded lightweight body-construction profiles."""

    LIGHTWEIGHT_ANIME_V1 = "lightweight_anime_v1"


class HairProfile(str, Enum):
    """Bounded deterministic hair-construction profiles."""

    SHOULDER_LENGTH_DARK_V1 = "shoulder_length_dark_v1"


class OutfitProfile(str, Enum):
    """Bounded deterministic outfit-construction profiles."""

    SIMPLE_EVERYDAY_V1 = "simple_everyday_v1"


class CharacterPaletteProfile(str, Enum):
    """Bounded character-specific palette profiles."""

    MOMO_DEFAULT_V1 = "momo_default_v1"


_STABLE_ID = re.compile(
    r"^[a-z][a-z0-9_-]*$"
)


def _scale(
    value: float,
    *,
    label: str,
) -> float:
    """Normalize one bounded production scale."""

    if (
        not isinstance(
            value,
            (int, float),
        )
        or isinstance(
            value,
            bool,
        )
    ):
        raise CharacterProductionSpecError(
            f"{label} must be numeric."
        )

    normalized = float(
        value
    )

    if not 0.5 <= normalized <= 1.5:
        raise CharacterProductionSpecError(
            f"{label} must be between 0.5 and 1.5."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterProportions:
    """Bounded silhouette proportions independent of Blender coordinates."""

    head_scale: float
    shoulder_scale: float
    torso_scale: float
    hip_scale: float
    limb_scale: float

    def __post_init__(
        self,
    ) -> None:
        """Validate deterministic production proportions."""

        for name in (
            "head_scale",
            "shoulder_scale",
            "torso_scale",
            "hip_scale",
            "limb_scale",
        ):
            object.__setattr__(
                self,
                name,
                _scale(
                    getattr(
                        self,
                        name,
                    ),
                    label=name,
                ),
            )


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterProductionSpec:
    """Describe how trusted production infrastructure should realize a character."""

    character_id: str
    variant_id: str
    production_profile_id: str
    rig_profile: RigProfile
    body_profile: BodyProfile
    hair_profile: HairProfile
    outfit_profile: OutfitProfile
    palette_profile: CharacterPaletteProfile
    proportions: CharacterProportions

    def __post_init__(
        self,
    ) -> None:
        """Validate the bounded compiled production contract."""

        for name in (
            "character_id",
            "variant_id",
            "production_profile_id",
        ):
            value = getattr(
                self,
                name,
            )

            if not isinstance(
                value,
                str,
            ):
                raise CharacterProductionSpecError(
                    f"{name} must be a string."
                )

            normalized = value.strip()

            if (
                not normalized
                or _STABLE_ID.fullmatch(
                    normalized
                )
                is None
            ):
                raise CharacterProductionSpecError(
                    f"{name} must be a stable lowercase identifier."
                )

            object.__setattr__(
                self,
                name,
                normalized,
            )

        typed_fields = (
            (
                "rig_profile",
                RigProfile,
            ),
            (
                "body_profile",
                BodyProfile,
            ),
            (
                "hair_profile",
                HairProfile,
            ),
            (
                "outfit_profile",
                OutfitProfile,
            ),
            (
                "palette_profile",
                CharacterPaletteProfile,
            ),
            (
                "proportions",
                CharacterProportions,
            ),
        )

        for name, expected_type in typed_fields:
            if not isinstance(
                getattr(
                    self,
                    name,
                ),
                expected_type,
            ):
                raise CharacterProductionSpecError(
                    f"{name} must be {expected_type.__name__}."
                )


@dataclass(
    frozen=True,
    slots=True,
)
class _CharacterProductionTemplate:
    """Internal trusted template selected by stable identity and variant IDs."""

    production_profile_id: str
    rig_profile: RigProfile
    body_profile: BodyProfile
    hair_profile: HairProfile
    outfit_profile: OutfitProfile
    palette_profile: CharacterPaletteProfile
    proportions: CharacterProportions


_MOMO_DEFAULT_TEMPLATE = _CharacterProductionTemplate(
    production_profile_id="momo_default_v1",
    rig_profile=RigProfile.STUDIO_HUMANOID_V1,
    body_profile=BodyProfile.LIGHTWEIGHT_ANIME_V1,
    hair_profile=HairProfile.SHOULDER_LENGTH_DARK_V1,
    outfit_profile=OutfitProfile.SIMPLE_EVERYDAY_V1,
    palette_profile=CharacterPaletteProfile.MOMO_DEFAULT_V1,
    proportions=CharacterProportions(
        head_scale=1.10,
        shoulder_scale=0.92,
        torso_scale=0.92,
        hip_scale=0.90,
        limb_scale=0.88,
    ),
)


_PRODUCTION_TEMPLATES = {
    (
        "momo",
        "default",
    ): _MOMO_DEFAULT_TEMPLATE,
}


def compile_character_production(
    identity: CharacterIdentity,
    variant: CharacterVariant,
) -> CharacterProductionSpec:
    """Compile semantic identity into one bounded deterministic production spec."""

    if not isinstance(
        identity,
        CharacterIdentity,
    ):
        raise CharacterProductionSpecError(
            "identity must be CharacterIdentity."
        )

    if not isinstance(
        variant,
        CharacterVariant,
    ):
        raise CharacterProductionSpecError(
            "variant must be CharacterVariant."
        )

    if (
        variant.character_id
        != identity.character_id
    ):
        raise CharacterProductionSpecError(
            "Character variant does not belong to the supplied identity."
        )

    key = (
        identity.character_id,
        variant.variant_id,
    )

    template = _PRODUCTION_TEMPLATES.get(
        key
    )

    if template is None:
        raise CharacterProductionSpecError(
            "No production profile registered for "
            f"'{identity.character_id}:{variant.variant_id}'."
        )

    return CharacterProductionSpec(
        character_id=identity.character_id,
        variant_id=variant.variant_id,
        production_profile_id=(
            template.production_profile_id
        ),
        rig_profile=template.rig_profile,
        body_profile=template.body_profile,
        hair_profile=template.hair_profile,
        outfit_profile=template.outfit_profile,
        palette_profile=template.palette_profile,
        proportions=template.proportions,
    )


CHARACTER_PRODUCTION_SCHEMA_VERSION = 1
CHARACTER_PRODUCTION_FILENAME = "character_production.json"


def character_production_to_data(
    spec: CharacterProductionSpec,
) -> dict[str, object]:
    """Convert one trusted production spec into versioned primitive data."""

    if not isinstance(
        spec,
        CharacterProductionSpec,
    ):
        raise CharacterProductionSpecError(
            "spec must be CharacterProductionSpec."
        )

    return {
        "schema_version": CHARACTER_PRODUCTION_SCHEMA_VERSION,
        "character_id": spec.character_id,
        "variant_id": spec.variant_id,
        "production_profile_id": spec.production_profile_id,
        "rig_profile": spec.rig_profile.value,
        "body_profile": spec.body_profile.value,
        "hair_profile": spec.hair_profile.value,
        "outfit_profile": spec.outfit_profile.value,
        "palette_profile": spec.palette_profile.value,
        "proportions": {
            "head_scale": spec.proportions.head_scale,
            "shoulder_scale": spec.proportions.shoulder_scale,
            "torso_scale": spec.proportions.torso_scale,
            "hip_scale": spec.proportions.hip_scale,
            "limb_scale": spec.proportions.limb_scale,
        },
    }


def character_production_to_json(
    spec: CharacterProductionSpec,
) -> str:
    """Serialize one production spec deterministically."""

    return json.dumps(
        character_production_to_data(
            spec
        ),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )


def character_production_from_json(
    raw_json: str,
) -> CharacterProductionSpec:
    """Reconstruct a trusted production spec from versioned JSON."""

    if not isinstance(
        raw_json,
        str,
    ):
        raise CharacterProductionSpecError(
            "Character production JSON must be a string."
        )

    if not raw_json.strip():
        raise CharacterProductionSpecError(
            "Character production JSON must not be empty."
        )

    try:
        data = json.loads(
            raw_json
        )
    except json.JSONDecodeError as exc:
        raise CharacterProductionSpecError(
            "Invalid character production JSON: "
            + str(exc)
        ) from exc

    return character_production_from_data(
        data
    )


def character_production_from_data(
    data: object,
) -> CharacterProductionSpec:
    """Reconstruct and validate one production spec from primitive data."""

    if not isinstance(
        data,
        dict,
    ):
        raise CharacterProductionSpecError(
            "Character production data must be an object."
        )

    expected = {
        "schema_version",
        "character_id",
        "variant_id",
        "production_profile_id",
        "rig_profile",
        "body_profile",
        "hair_profile",
        "outfit_profile",
        "palette_profile",
        "proportions",
    }

    actual = set(
        data
    )

    if actual != expected:
        missing = sorted(
            expected - actual
        )

        extra = sorted(
            actual - expected
        )

        details = []

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

        raise CharacterProductionSpecError(
            "Character production data has invalid fields: "
            + "; ".join(
                details
            )
        )

    version = data[
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
        raise CharacterProductionSpecError(
            "schema_version must be an integer."
        )

    if (
        version
        != CHARACTER_PRODUCTION_SCHEMA_VERSION
    ):
        raise CharacterProductionSpecError(
            "Unsupported character production schema version: "
            + str(version)
        )

    proportions_data = data[
        "proportions"
    ]

    if not isinstance(
        proportions_data,
        dict,
    ):
        raise CharacterProductionSpecError(
            "proportions must be an object."
        )

    proportion_fields = {
        "head_scale",
        "shoulder_scale",
        "torso_scale",
        "hip_scale",
        "limb_scale",
    }

    if set(
        proportions_data
    ) != proportion_fields:
        raise CharacterProductionSpecError(
            "proportions has invalid fields."
        )

    def required_text(
        key: str,
    ) -> str:
        value = data[
            key
        ]

        if not isinstance(
            value,
            str,
        ):
            raise CharacterProductionSpecError(
                f"{key} must be a string."
            )

        return value

    try:
        return CharacterProductionSpec(
            character_id=required_text(
                "character_id"
            ),
            variant_id=required_text(
                "variant_id"
            ),
            production_profile_id=required_text(
                "production_profile_id"
            ),
            rig_profile=RigProfile(
                required_text(
                    "rig_profile"
                )
            ),
            body_profile=BodyProfile(
                required_text(
                    "body_profile"
                )
            ),
            hair_profile=HairProfile(
                required_text(
                    "hair_profile"
                )
            ),
            outfit_profile=OutfitProfile(
                required_text(
                    "outfit_profile"
                )
            ),
            palette_profile=CharacterPaletteProfile(
                required_text(
                    "palette_profile"
                )
            ),
            proportions=CharacterProportions(
                head_scale=proportions_data[
                    "head_scale"
                ],
                shoulder_scale=proportions_data[
                    "shoulder_scale"
                ],
                torso_scale=proportions_data[
                    "torso_scale"
                ],
                hip_scale=proportions_data[
                    "hip_scale"
                ],
                limb_scale=proportions_data[
                    "limb_scale"
                ],
            ),
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        if isinstance(
            exc,
            CharacterProductionSpecError,
        ):
            raise

        raise CharacterProductionSpecError(
            "Serialized character production data "
            "violates the production contract: "
            + str(exc)
        ) from exc
