"""Studio local text-to-speech adapters."""

from kernel.adapters.tts.piper import (
    PiperTTSAdapter,
    PiperTTSError,
)


__all__ = [
    "PiperTTSAdapter",
    "PiperTTSError",
]
