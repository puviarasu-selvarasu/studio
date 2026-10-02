"""Studio Phase-11 language catalog."""

from __future__ import annotations

from kernel.languages.models import (
    LanguageIdentity,
)


SUPPORTED_LANGUAGES = (
    LanguageIdentity("en-US", "English", "English", "Latin"),
    LanguageIdentity("ta-IN", "Tamil", "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd", "Tamil"),
    LanguageIdentity("hi-IN", "Hindi", "\u0939\u093f\u0928\u094d\u0926\u0940", "Devanagari"),
    LanguageIdentity("ja-JP", "Japanese", "\u65e5\u672c\u8a9e", "Japanese"),
    LanguageIdentity("ko-KR", "Korean", "\ud55c\uad6d\uc5b4", "Hangul"),
    LanguageIdentity("zh-CN", "Mandarin Chinese", "\u4e2d\u6587", "Han"),
    LanguageIdentity("es-ES", "Spanish", "Espa\u00f1ol", "Latin"),
    LanguageIdentity("fr-FR", "French", "Fran\u00e7ais", "Latin"),
    LanguageIdentity("de-DE", "German", "Deutsch", "Latin"),
)


def get_language_identity(
    language_code: str,
) -> LanguageIdentity | None:
    if not isinstance(
        language_code,
        str,
    ):
        return None

    target = (
        language_code
        .strip()
        .replace("_", "-")
        .lower()
    )

    for language in SUPPORTED_LANGUAGES:
        candidate = (
            language.language_code
            .replace("_", "-")
            .lower()
        )

        if candidate == target:
            return language

    return None
