"""CPU-only language-neutral WAV energy analysis for Studio lip sync."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from kernel.acting import (
    LipSyncAnalysis,
    Viseme,
    VisemeCue,
)


class WavLipSyncError(
    RuntimeError
):
    """Raised when a local WAV cannot be analyzed safely."""


class WavLipSyncAnalyzer:
    """Derive low-cost limited-animation viseme timing from PCM energy."""

    def analyze(
        self,
        audio_path: Path,
        *,
        fps: int = 24,
        frame_step: int = 2,
    ) -> LipSyncAnalysis:
        """Analyze one WAV without cloud services or speech recognition."""

        audio_path = Path(
            audio_path
        )

        if fps <= 0:
            raise ValueError(
                "fps must be positive."
            )

        if frame_step <= 0:
            raise ValueError(
                "frame_step must be positive."
            )

        if not audio_path.is_file():
            raise WavLipSyncError(
                "WAV file does not exist: "
                + str(
                    audio_path
                )
            )

        try:
            with wave.open(
                str(
                    audio_path
                ),
                "rb",
            ) as wav:
                channels = (
                    wav.getnchannels()
                )

                sample_width = (
                    wav.getsampwidth()
                )

                sample_rate = (
                    wav.getframerate()
                )

                frame_count = (
                    wav.getnframes()
                )

                raw = wav.readframes(
                    frame_count
                )

        except (
            wave.Error,
            OSError,
        ) as exc:
            raise WavLipSyncError(
                "Unable to read PCM WAV."
            ) from exc

        if channels <= 0:
            raise WavLipSyncError(
                "WAV channel count is invalid."
            )

        if sample_rate <= 0:
            raise WavLipSyncError(
                "WAV sample rate is invalid."
            )

        if frame_count <= 0:
            raise WavLipSyncError(
                "WAV contains no audio frames."
            )

        samples = _decode_pcm(
            raw,
            sample_width,
        )

        expected_samples = (
            frame_count
            * channels
        )

        if (
            len(
                samples
            )
            != expected_samples
        ):
            raise WavLipSyncError(
                "PCM sample count does not match WAV metadata."
            )

        duration = (
            frame_count
            / sample_rate
        )

        end_frame = max(
            1,
            int(
                round(
                    duration
                    * fps
                )
            ),
        )

        window_frames = max(
            1,
            int(
                round(
                    sample_rate
                    * frame_step
                    / fps
                )
            ),
        )

        window_samples = (
            window_frames
            * channels
        )

        energies: list[
            float
        ] = []

        offsets = range(
            0,
            len(
                samples
            ),
            window_samples,
        )

        windows: list[
            tuple[
                int,
                tuple[
                    int,
                    ...,
                ],
            ]
        ] = []

        for index, offset in enumerate(
            offsets
        ):
            window = samples[
                offset:
                offset
                + window_samples
            ]

            if not window:
                continue

            windows.append(
                (
                    index,
                    window,
                )
            )

            square_mean = (
                sum(
                    sample
                    * sample
                    for sample
                    in window
                )
                / len(
                    window
                )
            )

            energies.append(
                math.sqrt(
                    square_mean
                )
            )

        peak = max(
            energies,
            default=0.0,
        )

        cues_by_frame: dict[
            int,
            VisemeCue,
        ] = {}

        for (
            sequence_index,
            (
                window_index,
                _window,
            ),
        ) in enumerate(
            windows
        ):
            energy = (
                energies[
                    sequence_index
                ]
            )

            normalized = (
                energy
                / peak
                if peak > 1.0
                else 0.0
            )

            frame = min(
                end_frame,
                1
                + (
                    window_index
                    * frame_step
                ),
            )

            viseme = (
                _viseme_for_energy(
                    normalized,
                    window_index,
                )
            )

            cues_by_frame[
                frame
            ] = VisemeCue(
                frame=frame,
                viseme=viseme,
                strength=min(
                    1.0,
                    max(
                        0.0,
                        normalized,
                    ),
                ),
            )

        cues_by_frame[
            end_frame
        ] = VisemeCue(
            frame=end_frame,
            viseme=Viseme.REST,
            strength=0.0,
        )

        return LipSyncAnalysis(
            fps=fps,
            end_frame=end_frame,
            duration_seconds=(
                duration
            ),
            visemes=tuple(
                cues_by_frame[
                    frame
                ]
                for frame
                in sorted(
                    cues_by_frame
                )
            ),
        )


def _decode_pcm(
    raw: bytes,
    sample_width: int,
) -> tuple[
    int,
    ...,
]:
    if sample_width == 1:
        return tuple(
            int(
                value
            )
            - 128
            for value
            in raw
        )

    if sample_width == 2:
        count = (
            len(
                raw
            )
            // 2
        )

        return tuple(
            struct.unpack(
                "<"
                + (
                    "h"
                    * count
                ),
                raw,
            )
        )

    if sample_width == 4:
        count = (
            len(
                raw
            )
            // 4
        )

        return tuple(
            struct.unpack(
                "<"
                + (
                    "i"
                    * count
                ),
                raw,
            )
        )

    raise WavLipSyncError(
        "Only 8-bit, 16-bit, or 32-bit PCM WAV is supported."
    )


def _viseme_for_energy(
    normalized: float,
    index: int,
) -> Viseme:
    if normalized < 0.08:
        return Viseme.REST

    if normalized < 0.22:
        return Viseme.CLOSED

    if normalized < 0.52:
        return Viseme.OPEN

    # V1 deliberately stays language-neutral.
    # High-energy windows alternate two graphic anime mouth forms.
    return (
        Viseme.WIDE
        if index % 2 == 0
        else Viseme.ROUND
    )
