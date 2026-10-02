"""Phase 15 pure-2D anime character art contract.

This module converts a stable personal capture profile into a renderer-neutral
character art specification.  It deliberately contains no Blender code: later
renderers consume this contract instead of inventing character design choices.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from kernel.characters.personal_capture import PersonalAnimeCaptureProfile


class Anime2DDesignError(ValueError):
    """Raised when a pure-2D character art specification is invalid."""


STYLE_ID = "studio_retro_modern_cel_v1"
ART_MODE = "pure_2d"
SCHEMA_VERSION = 1

VIEW_KINDS = frozenset(
    {
        "front",
        "three_quarter_left",
        "three_quarter_right",
        "profile_left",
        "profile_right",
    }
)

EXPRESSION_KINDS = frozenset(
    {
        "neutral",
        "warm",
        "smile",
        "sad",
        "fearful",
        "angry",
        "determined",
        "surprised",
        "tired",
        "speaking",
    }
)

EYE_DIRECTIONS = frozenset(
    {
        "center",
        "left",
        "right",
        "up",
        "down",
    }
)

_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _required_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Anime2DDesignError(field + " must not be blank.")
    return value.strip()


def _hex_color(value: str, field: str) -> str:
    normalized = _required_text(value, field).upper()
    if _HEX.fullmatch(normalized) is None:
        raise Anime2DDesignError(field + " must use #RRGGBB.")
    return normalized


def _bounded(
    value: float,
    field: str,
    minimum: float,
    maximum: float,
) -> float:
    number = float(value)
    if not minimum <= number <= maximum:
        raise Anime2DDesignError(
            field
            + " must be between "
            + str(minimum)
            + " and "
            + str(maximum)
            + "."
        )
    return number


def _choice(value: str, allowed: frozenset[str], field: str) -> str:
    normalized = _required_text(value, field)
    if normalized not in allowed:
        raise Anime2DDesignError(field + " contains an unsupported value.")
    return normalized


def _multiply_hex(value: str, factor: float) -> str:
    source = _hex_color(value, "color")
    channels = [
        int(source[index : index + 2], 16)
        for index in (1, 3, 5)
    ]
    scaled = [
        max(0, min(255, round(channel * factor)))
        for channel in channels
    ]
    return "#" + "".join(f"{channel:02X}" for channel in scaled)


def _stable_seed(character_id: str) -> int:
    digest = hashlib.sha256(character_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big")


@dataclass(frozen=True, slots=True)
class Anime2DInkSpec:
    outer_width: float = 0.040
    feature_width: float = 0.026
    detail_width: float = 0.016
    taper: float = 0.58
    wobble: float = 0.010

    def __post_init__(self) -> None:
        outer = _bounded(self.outer_width, "outer_width", 0.020, 0.080)
        feature = _bounded(self.feature_width, "feature_width", 0.010, 0.060)
        detail = _bounded(self.detail_width, "detail_width", 0.006, 0.040)
        taper = _bounded(self.taper, "taper", 0.10, 0.90)
        wobble = _bounded(self.wobble, "wobble", 0.0, 0.030)

        if not outer > feature > detail:
            raise Anime2DDesignError(
                "Ink widths must descend from outer to feature to detail."
            )

        object.__setattr__(self, "outer_width", outer)
        object.__setattr__(self, "feature_width", feature)
        object.__setattr__(self, "detail_width", detail)
        object.__setattr__(self, "taper", taper)
        object.__setattr__(self, "wobble", wobble)


@dataclass(frozen=True, slots=True)
class Anime2DCelSpec:
    shadow_layers: int = 2
    highlight_layers: int = 1
    shadow_strength: float = 0.68
    hard_edges: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.shadow_layers, int) or not 1 <= self.shadow_layers <= 3:
            raise Anime2DDesignError("shadow_layers must be between 1 and 3.")
        if not isinstance(self.highlight_layers, int) or not 0 <= self.highlight_layers <= 2:
            raise Anime2DDesignError("highlight_layers must be between 0 and 2.")
        object.__setattr__(
            self,
            "shadow_strength",
            _bounded(self.shadow_strength, "shadow_strength", 0.40, 0.85),
        )
        if self.hard_edges is not True:
            raise Anime2DDesignError("Studio cel shading requires hard_edges=True.")


@dataclass(frozen=True, slots=True)
class Anime2DViewSpec:
    view: str
    expression: str
    eye_direction: str = "center"
    head_tilt_degrees: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "view", _choice(self.view, VIEW_KINDS, "view"))
        object.__setattr__(
            self,
            "expression",
            _choice(self.expression, EXPRESSION_KINDS, "expression"),
        )
        object.__setattr__(
            self,
            "eye_direction",
            _choice(self.eye_direction, EYE_DIRECTIONS, "eye_direction"),
        )
        object.__setattr__(
            self,
            "head_tilt_degrees",
            _bounded(self.head_tilt_degrees, "head_tilt_degrees", -15.0, 15.0),
        )


@dataclass(frozen=True, slots=True)
class Anime2DCharacterDesign:
    character_id: str
    display_name: str
    source_profile_id: str

    face_shape: str
    hair_shape: str
    hair_texture: str
    brow_style: str
    eye_shape: str
    nose_profile: str
    facial_hair_style: str
    body_silhouette: str

    skin_color: str
    skin_shadow_color: str
    hair_color: str
    eye_color: str
    outfit_color: str
    ink_color: str

    shoulder_scale: float
    torso_scale: float
    head_scale: float

    ink: Anime2DInkSpec
    cel: Anime2DCelSpec
    acceptance_views: tuple[Anime2DViewSpec, ...]
    asymmetry_seed: int

    style_id: str = STYLE_ID
    art_mode: str = ART_MODE

    def __post_init__(self) -> None:
        for field in (
            "character_id",
            "display_name",
            "source_profile_id",
            "face_shape",
            "hair_shape",
            "hair_texture",
            "brow_style",
            "eye_shape",
            "nose_profile",
            "facial_hair_style",
            "body_silhouette",
            "style_id",
            "art_mode",
        ):
            object.__setattr__(
                self,
                field,
                _required_text(getattr(self, field), field),
            )

        if self.style_id != STYLE_ID:
            raise Anime2DDesignError("Unsupported style_id.")
        if self.art_mode != ART_MODE:
            raise Anime2DDesignError("art_mode must be pure_2d.")

        for field in (
            "skin_color",
            "skin_shadow_color",
            "hair_color",
            "eye_color",
            "outfit_color",
            "ink_color",
        ):
            object.__setattr__(
                self,
                field,
                _hex_color(getattr(self, field), field),
            )

        object.__setattr__(
            self,
            "shoulder_scale",
            _bounded(self.shoulder_scale, "shoulder_scale", 0.80, 1.30),
        )
        object.__setattr__(
            self,
            "torso_scale",
            _bounded(self.torso_scale, "torso_scale", 0.80, 1.25),
        )
        object.__setattr__(
            self,
            "head_scale",
            _bounded(self.head_scale, "head_scale", 0.85, 1.15),
        )

        if not isinstance(self.acceptance_views, tuple) or len(self.acceptance_views) < 3:
            raise Anime2DDesignError("At least three acceptance views are required.")

        keys = tuple(
            (item.view, item.expression)
            for item in self.acceptance_views
        )
        if len(keys) != len(set(keys)):
            raise Anime2DDesignError("Acceptance view/expression pairs must be unique.")

        if not isinstance(self.asymmetry_seed, int) or self.asymmetry_seed < 0:
            raise Anime2DDesignError("asymmetry_seed must be a non-negative integer.")


DEFAULT_ACCEPTANCE_VIEWS = (
    Anime2DViewSpec(
        view="front",
        expression="neutral",
    ),
    Anime2DViewSpec(
        view="three_quarter_right",
        expression="neutral",
    ),
    Anime2DViewSpec(
        view="three_quarter_left",
        expression="determined",
        eye_direction="right",
        head_tilt_degrees=-2.0,
    ),
)


def compile_anime_2d_design(
    profile: PersonalAnimeCaptureProfile,
) -> Anime2DCharacterDesign:
    """Compile Phase-14 capture data into the Phase-15 art contract."""

    if not isinstance(profile, PersonalAnimeCaptureProfile):
        raise TypeError("profile must be PersonalAnimeCaptureProfile.")

    return Anime2DCharacterDesign(
        character_id=profile.character_id,
        display_name=profile.display_name,
        source_profile_id=profile.profile_id,
        face_shape=profile.face_shape,
        hair_shape=profile.hair_shape,
        hair_texture=profile.hair_texture,
        brow_style=profile.brow_style,
        eye_shape=profile.eye_shape,
        nose_profile=profile.nose_profile,
        facial_hair_style=profile.facial_hair_style,
        body_silhouette=profile.body_silhouette,
        skin_color=profile.skin_color,
        skin_shadow_color=_multiply_hex(profile.skin_color, 0.68),
        hair_color=profile.hair_color,
        eye_color=profile.eye_color,
        outfit_color=profile.outfit_color,
        ink_color="#17131A",
        shoulder_scale=profile.shoulder_scale,
        torso_scale=profile.torso_scale,
        head_scale=profile.head_scale,
        ink=Anime2DInkSpec(),
        cel=Anime2DCelSpec(),
        acceptance_views=DEFAULT_ACCEPTANCE_VIEWS,
        asymmetry_seed=_stable_seed(profile.character_id),
    )


def anime_2d_design_to_data(
    design: Anime2DCharacterDesign,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "style_id": design.style_id,
        "art_mode": design.art_mode,
        "character_id": design.character_id,
        "display_name": design.display_name,
        "source_profile_id": design.source_profile_id,
        "features": {
            "face_shape": design.face_shape,
            "hair_shape": design.hair_shape,
            "hair_texture": design.hair_texture,
            "brow_style": design.brow_style,
            "eye_shape": design.eye_shape,
            "nose_profile": design.nose_profile,
            "facial_hair_style": design.facial_hair_style,
            "body_silhouette": design.body_silhouette,
        },
        "palette": {
            "skin_color": design.skin_color,
            "skin_shadow_color": design.skin_shadow_color,
            "hair_color": design.hair_color,
            "eye_color": design.eye_color,
            "outfit_color": design.outfit_color,
            "ink_color": design.ink_color,
        },
        "proportions": {
            "shoulder_scale": design.shoulder_scale,
            "torso_scale": design.torso_scale,
            "head_scale": design.head_scale,
        },
        "ink": {
            "outer_width": design.ink.outer_width,
            "feature_width": design.ink.feature_width,
            "detail_width": design.ink.detail_width,
            "taper": design.ink.taper,
            "wobble": design.ink.wobble,
        },
        "cel": {
            "shadow_layers": design.cel.shadow_layers,
            "highlight_layers": design.cel.highlight_layers,
            "shadow_strength": design.cel.shadow_strength,
            "hard_edges": design.cel.hard_edges,
        },
        "acceptance_views": [
            {
                "view": item.view,
                "expression": item.expression,
                "eye_direction": item.eye_direction,
                "head_tilt_degrees": item.head_tilt_degrees,
            }
            for item in design.acceptance_views
        ],
        "asymmetry_seed": design.asymmetry_seed,
    }


def anime_2d_design_to_json(
    design: Anime2DCharacterDesign,
) -> str:
    return json.dumps(
        anime_2d_design_to_data(design),
        indent=2,
        sort_keys=True,
    ) + "\n"


def anime_2d_design_from_data(
    data: dict[str, object],
) -> Anime2DCharacterDesign:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise Anime2DDesignError("Unsupported schema_version.")

    features = data.get("features")
    palette = data.get("palette")
    proportions = data.get("proportions")
    ink = data.get("ink")
    cel = data.get("cel")
    acceptance_views = data.get("acceptance_views")

    if not all(
        isinstance(value, dict)
        for value in (features, palette, proportions, ink, cel)
    ):
        raise Anime2DDesignError("Nested design sections must be objects.")
    if not isinstance(acceptance_views, list):
        raise Anime2DDesignError("acceptance_views must be a list.")

    try:
        return Anime2DCharacterDesign(
            character_id=str(data["character_id"]),
            display_name=str(data["display_name"]),
            source_profile_id=str(data["source_profile_id"]),
            face_shape=str(features["face_shape"]),
            hair_shape=str(features["hair_shape"]),
            hair_texture=str(features["hair_texture"]),
            brow_style=str(features["brow_style"]),
            eye_shape=str(features["eye_shape"]),
            nose_profile=str(features["nose_profile"]),
            facial_hair_style=str(features["facial_hair_style"]),
            body_silhouette=str(features["body_silhouette"]),
            skin_color=str(palette["skin_color"]),
            skin_shadow_color=str(palette["skin_shadow_color"]),
            hair_color=str(palette["hair_color"]),
            eye_color=str(palette["eye_color"]),
            outfit_color=str(palette["outfit_color"]),
            ink_color=str(palette["ink_color"]),
            shoulder_scale=float(proportions["shoulder_scale"]),
            torso_scale=float(proportions["torso_scale"]),
            head_scale=float(proportions["head_scale"]),
            ink=Anime2DInkSpec(
                outer_width=float(ink["outer_width"]),
                feature_width=float(ink["feature_width"]),
                detail_width=float(ink["detail_width"]),
                taper=float(ink["taper"]),
                wobble=float(ink["wobble"]),
            ),
            cel=Anime2DCelSpec(
                shadow_layers=int(cel["shadow_layers"]),
                highlight_layers=int(cel["highlight_layers"]),
                shadow_strength=float(cel["shadow_strength"]),
                hard_edges=cel["hard_edges"],
            ),
            acceptance_views=tuple(
                Anime2DViewSpec(
                    view=str(item["view"]),
                    expression=str(item["expression"]),
                    eye_direction=str(item["eye_direction"]),
                    head_tilt_degrees=float(item["head_tilt_degrees"]),
                )
                for item in acceptance_views
                if isinstance(item, dict)
            ),
            asymmetry_seed=int(data["asymmetry_seed"]),
            style_id=str(data["style_id"]),
            art_mode=str(data["art_mode"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, Anime2DDesignError):
            raise
        raise Anime2DDesignError("Malformed anime 2D design data.") from exc


def anime_2d_design_from_json(source: str) -> Anime2DCharacterDesign:
    try:
        data = json.loads(source)
    except json.JSONDecodeError as exc:
        raise Anime2DDesignError("Invalid anime 2D design JSON.") from exc

    if not isinstance(data, dict):
        raise Anime2DDesignError("Anime 2D design JSON must contain an object.")

    return anime_2d_design_from_data(data)
