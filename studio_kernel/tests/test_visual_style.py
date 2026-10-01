"""Tests for Studio Visual Style System V1 contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from kernel.visual_style import (
    ANIME_CEL_V1,
    AtmosphereProfile,
    BackgroundProfile,
    CameraPresentationProfile,
    CelProfile,
    ColorRGB,
    CompositingProfile,
    LightingProfile,
    LineProfile,
    RenderProfile,
    VisualStyleError,
    get_visual_style,
    list_visual_style_ids,
)


MODULE = (
    Path(__file__).parents[1]
    / "kernel"
    / "visual_style.py"
)


def test_anime_cel_v1_is_registered() -> None:
    assert list_visual_style_ids() == (
        "anime_cel_v1",
    )

    assert (
        get_visual_style(
            "anime_cel_v1"
        )
        is ANIME_CEL_V1
    )


def test_anime_cel_v1_uses_expected_visual_grammar() -> None:
    style = ANIME_CEL_V1

    assert (
        style.render_profile
        is RenderProfile.WORKBENCH_CEL
    )

    assert (
        style.cel_profile
        is CelProfile.THREE_TONE
    )

    assert style.cel_levels == 3

    assert (
        style.line_profile
        is LineProfile.BOLD_INK
    )

    assert style.line_width_px == 2.0

    assert (
        style.lighting_profile
        is LightingProfile.WARM_KEY_COOL_FILL
    )

    assert (
        style.background_profile
        is BackgroundProfile.LAYERED_2_5D
    )

    assert style.background_depth_layers == 3

    assert (
        style.atmosphere_profile
        is AtmosphereProfile.RESTRAINED
    )

    assert (
        style.camera_profile
        is CameraPresentationProfile.ANIME_CINEMATIC
    )

    assert (
        style.compositing_profile
        is CompositingProfile.CLEAN_CEL
    )


def test_visual_palette_colors_are_normalized() -> None:
    palette = ANIME_CEL_V1.palette

    colors = (
        palette.ink,
        palette.character_base,
        palette.character_shadow,
        palette.character_highlight,
        palette.accent,
        palette.warm_key,
        palette.cool_fill,
        palette.ground,
        palette.background_near,
        palette.background_mid,
        palette.background_far,
    )

    for color in colors:
        assert isinstance(
            color,
            ColorRGB,
        )

        assert all(
            0.0 <= channel <= 1.0
            for channel
            in color.as_tuple()
        )


def test_color_contract_rejects_invalid_channel() -> None:
    with pytest.raises(
        VisualStyleError,
        match="between 0 and 1",
    ):
        ColorRGB(
            1.25,
            0.5,
            0.5,
        )


def test_visual_style_is_immutable() -> None:
    with pytest.raises(
        FrozenInstanceError
    ):
        ANIME_CEL_V1.style_id = "changed"  # type: ignore[misc]


def test_unknown_visual_style_is_rejected() -> None:
    with pytest.raises(
        VisualStyleError,
        match="Unsupported visual style",
    ):
        get_visual_style(
            "unknown_style"
        )


def test_visual_style_contract_has_no_runtime_dependencies() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    assert "import bpy" not in source
    assert "from bpy" not in source

    assert "ollama" not in source.lower()
    assert "pydantic" not in source.lower()

    assert "exec(" not in source
    assert "eval(" not in source

def test_anime_cel_v1_has_warm_key_and_cool_fill_palette() -> None:
    palette = ANIME_CEL_V1.palette

    assert palette.warm_key.as_tuple() == (
        1.0,
        0.62,
        0.30,
    )

    assert palette.cool_fill.as_tuple() == (
        0.26,
        0.44,
        0.82,
    )
