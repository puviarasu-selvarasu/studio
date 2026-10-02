"""Language-specific runtime voices behind semantic voice identity."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.languages import (
    get_language_identity,
)
from kernel.voices.catalog import (
    get_voice_identity,
)


class VoiceLocalizationError(
    ValueError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class LocalizedVoiceIdentity:
    base_voice_id: str
    language_code: str
    production_voice_id: str
    provider_id: str

    def __post_init__(
        self,
    ) -> None:
        if (
            get_voice_identity(
                self.base_voice_id
            )
            is None
        ):
            raise VoiceLocalizationError(
                "Unknown base voice."
            )

        language = (
            get_language_identity(
                self.language_code
            )
        )

        if language is None:
            raise VoiceLocalizationError(
                "Unsupported language."
            )

        object.__setattr__(
            self,
            "language_code",
            language.language_code,
        )


STUDIO_VOICE_01_LOCALIZATIONS = tuple(
    LocalizedVoiceIdentity(
        "studio_voice_01",
        language,
        production_voice,
        "piper",
    )
    for language, production_voice
    in (
        ("en-US", "studio_voice_01_en"),
        ("ta-IN", "studio_voice_01_ta"),
        ("hi-IN", "studio_voice_01_hi"),
        ("ja-JP", "studio_voice_01_ja"),
        ("ko-KR", "studio_voice_01_ko"),
        ("zh-CN", "studio_voice_01_zh"),
        ("es-ES", "studio_voice_01_es"),
        ("fr-FR", "studio_voice_01_fr"),
        ("de-DE", "studio_voice_01_de"),
    )
)


def get_localized_voice_identity(
    base_voice_id: str,
    language_code: str,
) -> LocalizedVoiceIdentity | None:
    language = (
        get_language_identity(
            language_code
        )
    )

    if language is None:
        return None

    for voice in STUDIO_VOICE_01_LOCALIZATIONS:
        if (
            voice.base_voice_id
            == base_voice_id
            and voice.language_code
            == language.language_code
        ):
            return voice

    return None
