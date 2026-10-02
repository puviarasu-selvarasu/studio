"""Tests for CPU-only WAV lip-sync analysis."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import pytest

from kernel.acting import (
    Viseme,
)
from kernel.adapters.audio.wav_lipsync import (
    WavLipSyncAnalyzer,
    WavLipSyncError,
)


def _write_test_wav(
    path: Path,
) -> None:
    sample_rate = 16000

    samples: list[
        int
    ] = []

    segments = (
        (0.20, 0),
        (0.25, 2500),
        (0.35, 12000),
        (0.20, 0),
    )

    phase = 0

    for duration, amplitude in segments:
        count = int(
            sample_rate
            * duration
        )

        for index in range(
            count
        ):
            value = (
                int(
                    amplitude
                    * math.sin(
                        2.0
                        * math.pi
                        * 180.0
                        * (
                            phase
                            + index
                        )
                        / sample_rate
                    )
                )
                if amplitude
                else 0
            )

            samples.append(
                value
            )

        phase += count

    with wave.open(
        str(
            path
        ),
        "wb",
    ) as wav:
        wav.setnchannels(
            1
        )

        wav.setsampwidth(
            2
        )

        wav.setframerate(
            sample_rate
        )

        wav.writeframes(
            struct.pack(
                "<"
                + (
                    "h"
                    * len(
                        samples
                    )
                ),
                *samples,
            )
        )


def test_wav_analyzer_generates_language_neutral_visemes(
    tmp_path: Path,
) -> None:
    audio = (
        tmp_path
        / "dialogue.wav"
    )

    _write_test_wav(
        audio
    )

    result = WavLipSyncAnalyzer().analyze(
        audio,
        fps=24,
        frame_step=2,
    )

    shapes = {
        cue.viseme
        for cue
        in result.visemes
    }

    assert Viseme.REST in shapes

    assert (
        Viseme.OPEN in shapes
        or Viseme.WIDE in shapes
        or Viseme.ROUND in shapes
    )

    assert result.end_frame == 24

    assert (
        result.visemes[
            -1
        ].viseme
        is Viseme.REST
    )


def test_wav_analyzer_rejects_missing_file(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        WavLipSyncError,
        match="does not exist",
    ):
        WavLipSyncAnalyzer().analyze(
            tmp_path
            / "missing.wav"
        )


def test_wav_analyzer_rejects_invalid_frame_step(
    tmp_path: Path,
) -> None:
    audio = (
        tmp_path
        / "dialogue.wav"
    )

    _write_test_wav(
        audio
    )

    with pytest.raises(
        ValueError,
        match="frame_step",
    ):
        WavLipSyncAnalyzer().analyze(
            audio,
            frame_step=0,
        )
