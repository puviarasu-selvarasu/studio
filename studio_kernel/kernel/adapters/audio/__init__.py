"""Studio local CPU audio-analysis adapters."""

from kernel.adapters.audio.wav_lipsync import (
    WavLipSyncAnalyzer,
    WavLipSyncError,
)


__all__ = [
    "WavLipSyncAnalyzer",
    "WavLipSyncError",
]
