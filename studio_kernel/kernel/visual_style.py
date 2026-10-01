"""Pure trusted visual-style contract for Studio.

This module describes WHAT visual language Studio should use.

It deliberately contains no Blender API calls, shader-node construction,
render execution, AI calls, or arbitrary generated code. Blender adapters
will later translate these bounded symbolic choices into deterministic
production operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Mapping


class VisualStyleError(ValueError):
    """Represent an invalid or unsupported Studio visual style."""


class RenderProfile(str, Enum):
    """Bounded Studio rendering profiles."""

    WORKBENCH_CEL = "workbench_cel"


class CelProfile(str, Enum):
    """Bounded cel-shading languages."""

    THREE_TONE = "three_tone"


class LineProfile(str, Enum):
    """Bounded line-treatment languages."""

    BOLD_INK = "bold_ink"


class LightingProfile(str, Enum):
    """Bounded anime-lighting languages."""

    WARM_KEY_COOL_FILL = "warm_key_cool_fill"


class BackgroundProfile(str, Enum):
    """Bounded environment-depth languages."""

    LAYERED_2_5D = "layered_2_5d"


class AtmosphereProfile(str, Enum):
    """Bounded atmosphere languages."""

    RESTRAINED = "restrained"


class CameraPresentationProfile(str, Enum):
    """Bounded photographic presentation languages."""

    ANIME_CINEMATIC = "anime_cinematic"


class CompositingProfile(str, Enum):
    """Bounded post-processing languages."""

    CLEAN_CEL = "clean_cel"


@dataclass(
    frozen=True,
    slots=True,
)
class ColorRGB:
    """Represent one normalized linear-style RGB triplet."""

    r: float
    g: float
    b: float

    def __post_init__(self) -> None:
        for channel_name in (
            "r",
            "g",
            "b",
        ):
            raw_value = getattr(
                self,
                channel_name,
            )

            if (
                isinstance(raw_value, bool)
                or not isinstance(
                    raw_value,
                    (
                        int,
                        float,
                    ),
                )
            ):
                raise VisualStyleError(
                    f"Color channel {channel_name} "
                    "must be numeric."
                )

            value = float(
                raw_value
            )

            if (
                not isfinite(value)
                or value < 0.0
                or value > 1.0
            ):
                raise VisualStyleError(
                    f"Color channel {channel_name} "
                    "must be between 0 and 1."
                )

            object.__setattr__(
                self,
                channel_name,
                value,
            )

    def as_tuple(
        self,
    ) -> tuple[
        float,
        float,
        float,
    ]:
        """Return the color as a deterministic tuple."""

        return (
            self.r,
            self.g,
            self.b,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class VisualPalette:
    """Hold the Studio-owned palette for one visual style."""

    ink: ColorRGB
    character_base: ColorRGB
    character_shadow: ColorRGB
    character_highlight: ColorRGB
    accent: ColorRGB
    warm_key: ColorRGB
    cool_fill: ColorRGB
    ground: ColorRGB
    background_near: ColorRGB
    background_mid: ColorRGB
    background_far: ColorRGB


@dataclass(
    frozen=True,
    slots=True,
)
class VisualStyle:
    """Describe one trusted Studio visual-production language."""

    style_id: str

    render_profile: RenderProfile

    cel_profile: CelProfile
    cel_levels: int

    line_profile: LineProfile
    line_width_px: float

    lighting_profile: LightingProfile

    background_profile: BackgroundProfile
    background_depth_layers: int

    atmosphere_profile: AtmosphereProfile

    camera_profile: CameraPresentationProfile

    compositing_profile: CompositingProfile

    palette: VisualPalette

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.style_id,
                str,
            )
            or not self.style_id.strip()
        ):
            raise VisualStyleError(
                "Visual style ID must not be empty."
            )

        if self.style_id != self.style_id.strip():
            raise VisualStyleError(
                "Visual style ID must not contain "
                "leading or trailing whitespace."
            )

        enum_fields = (
            (
                "render_profile",
                self.render_profile,
                RenderProfile,
            ),
            (
                "cel_profile",
                self.cel_profile,
                CelProfile,
            ),
            (
                "line_profile",
                self.line_profile,
                LineProfile,
            ),
            (
                "lighting_profile",
                self.lighting_profile,
                LightingProfile,
            ),
            (
                "background_profile",
                self.background_profile,
                BackgroundProfile,
            ),
            (
                "atmosphere_profile",
                self.atmosphere_profile,
                AtmosphereProfile,
            ),
            (
                "camera_profile",
                self.camera_profile,
                CameraPresentationProfile,
            ),
            (
                "compositing_profile",
                self.compositing_profile,
                CompositingProfile,
            ),
        )

        for (
            field_name,
            value,
            expected_type,
        ) in enum_fields:
            if not isinstance(
                value,
                expected_type,
            ):
                raise VisualStyleError(
                    f"{field_name} must use a "
                    "supported Studio profile."
                )

        if self.cel_levels not in {
            2,
            3,
        }:
            raise VisualStyleError(
                "Cel shading must use 2 or 3 levels."
            )

        if (
            isinstance(
                self.line_width_px,
                bool,
            )
            or not isinstance(
                self.line_width_px,
                (
                    int,
                    float,
                ),
            )
        ):
            raise VisualStyleError(
                "Line width must be numeric."
            )

        line_width = float(
            self.line_width_px
        )

        if (
            not isfinite(line_width)
            or line_width <= 0.0
            or line_width > 6.0
        ):
            raise VisualStyleError(
                "Line width must be greater than 0 "
                "and at most 6 pixels."
            )

        object.__setattr__(
            self,
            "line_width_px",
            line_width,
        )

        if (
            self.background_depth_layers < 2
            or self.background_depth_layers > 4
        ):
            raise VisualStyleError(
                "Background depth must use "
                "between 2 and 4 layers."
            )

        if not isinstance(
            self.palette,
            VisualPalette,
        ):
            raise VisualStyleError(
                "Visual style requires a VisualPalette."
            )


ANIME_CEL_V1 = VisualStyle(
    style_id="anime_cel_v1",

    render_profile=(
        RenderProfile.WORKBENCH_CEL
    ),

    cel_profile=(
        CelProfile.THREE_TONE
    ),
    cel_levels=3,

    line_profile=(
        LineProfile.BOLD_INK
    ),
    line_width_px=2.0,

    lighting_profile=(
        LightingProfile.WARM_KEY_COOL_FILL
    ),

    background_profile=(
        BackgroundProfile.LAYERED_2_5D
    ),
    background_depth_layers=3,

    atmosphere_profile=(
        AtmosphereProfile.RESTRAINED
    ),

    camera_profile=(
        CameraPresentationProfile.ANIME_CINEMATIC
    ),

    compositing_profile=(
        CompositingProfile.CLEAN_CEL
    ),

    palette=VisualPalette(
        ink=ColorRGB(
            0.020,
            0.025,
            0.035,
        ),
        character_base=ColorRGB(
            0.680,
            0.580,
            0.480,
        ),
        character_shadow=ColorRGB(
            0.240,
            0.200,
            0.220,
        ),
        character_highlight=ColorRGB(
            0.900,
            0.820,
            0.680,
        ),
        accent=ColorRGB(
            0.650,
            0.080,
            0.080,
        ),
        warm_key=ColorRGB(
            1.000,
            0.620,
            0.300,
        ),
        cool_fill=ColorRGB(
            0.260,
            0.440,
            0.820,
        ),
        ground=ColorRGB(
            0.100,
            0.120,
            0.140,
        ),
        background_near=ColorRGB(
            0.160,
            0.190,
            0.220,
        ),
        background_mid=ColorRGB(
            0.090,
            0.120,
            0.160,
        ),
        background_far=ColorRGB(
            0.045,
            0.060,
            0.090,
        ),
    ),
)


_VISUAL_STYLES: Mapping[
    str,
    VisualStyle,
] = MappingProxyType(
    {
        ANIME_CEL_V1.style_id: (
            ANIME_CEL_V1
        ),
    }
)


def list_visual_style_ids(
) -> tuple[str, ...]:
    """Return stable trusted Studio visual-style IDs."""

    return tuple(
        _VISUAL_STYLES
    )


def get_visual_style(
    style_id: str,
) -> VisualStyle:
    """Resolve one trusted visual style by exact ID."""

    if not isinstance(
        style_id,
        str,
    ):
        raise VisualStyleError(
            "Visual style ID must be a string."
        )

    normalized = style_id.strip()

    if not normalized:
        raise VisualStyleError(
            "Visual style ID must not be empty."
        )

    style = _VISUAL_STYLES.get(
        normalized
    )

    if style is None:
        raise VisualStyleError(
            f"Unsupported visual style: {normalized}"
        )

    return style
