"""Canonical reusable Studio voice identities."""

from __future__ import annotations

from kernel.voices.models import (
    VoiceIdentity,
)


STUDIO_VOICE_01 = VoiceIdentity(
    voice_id="studio_voice_01",
    language_code="en-US",
    traits=(
        "warm",
        "clear",
        "youthful",
        "restrained",
    ),
)


STUDIO_VOICE_02 = VoiceIdentity(
    voice_id="studio_voice_02",
    language_code="en-US",
    traits=(
        "grounded",
        "firm",
        "measured",
        "contrasting",
    ),
)


VOICE_IDENTITIES = (
    STUDIO_VOICE_01,
    STUDIO_VOICE_02,
)


def get_voice_identity(
    voice_id: str,
) -> VoiceIdentity | None:
    """Resolve one semantic voice identity."""

    normalized = voice_id.strip()

    for identity in VOICE_IDENTITIES:
        if (
            identity.voice_id
            == normalized
        ):
            return identity

    return None
