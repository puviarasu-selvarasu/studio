"""Trusted compilation of acting intent to bounded Piper controls."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.voices import (
    VoicePerformancePlan,
)


@dataclass(
    frozen=True,
    slots=True,
)
class PiperSynthesisControls:
    length_scale: float
    noise_scale: float
    noise_w_scale: float
    volume: float
    sentence_silence: float


def piper_controls_for_performance(
    plan: VoicePerformancePlan,
) -> PiperSynthesisControls:
    """Translate semantic acting into conservative synthesis controls."""

    emotion = (
        plan.emotion.value
    )

    pace = (
        plan.pace.value
    )

    energy = (
        plan.energy.value
    )

    emotion_profile = {
        "neutral": (
            1.00,
            0.55,
            0.65,
            1.00,
            0.035,
        ),
        "warm": (
            0.98,
            0.50,
            0.62,
            1.00,
            0.045,
        ),
        "joyful": (
            0.92,
            0.66,
            0.74,
            1.06,
            0.020,
        ),
        "sad": (
            1.12,
            0.43,
            0.54,
            0.92,
            0.080,
        ),
        "angry": (
            0.88,
            0.72,
            0.75,
            1.12,
            0.015,
        ),
        "fearful": (
            1.04,
            0.78,
            0.82,
            0.98,
            0.060,
        ),
        "serious": (
            1.04,
            0.45,
            0.56,
            1.02,
            0.040,
        ),
        "determined": (
            0.94,
            0.53,
            0.61,
            1.08,
            0.025,
        ),
    }[
        emotion
    ]

    pace_factor = {
        "slow": 1.10,
        "natural": 1.00,
        "fast": 0.91,
    }.get(
        pace,
        1.00,
    )

    energy_volume = {
        "low": 0.94,
        "medium": 1.00,
        "high": 1.08,
    }.get(
        energy,
        1.00,
    )

    (
        length_scale,
        noise_scale,
        noise_w_scale,
        volume,
        silence,
    ) = emotion_profile

    return PiperSynthesisControls(
        length_scale=_clamp(
            length_scale
            * pace_factor,
            0.72,
            1.35,
        ),
        noise_scale=_clamp(
            noise_scale,
            0.25,
            0.90,
        ),
        noise_w_scale=_clamp(
            noise_w_scale,
            0.30,
            0.90,
        ),
        volume=_clamp(
            volume
            * energy_volume,
            0.75,
            1.25,
        ),
        sentence_silence=_clamp(
            silence,
            0.0,
            0.15,
        ),
    )


def _clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    return max(
        minimum,
        min(
            maximum,
            float(
                value
            ),
        ),
    )
