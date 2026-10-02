from kernel.languages import (
    SUPPORTED_LANGUAGES,
    get_language_identity,
)
from kernel.voices.localization import (
    STUDIO_VOICE_01_LOCALIZATIONS,
    get_localized_voice_identity,
)


EXPECTED = {
    "en-US",
    "ta-IN",
    "hi-IN",
    "ja-JP",
    "ko-KR",
    "zh-CN",
    "es-ES",
    "fr-FR",
    "de-DE",
}


def test_phase11_exact_nine_languages() -> None:
    assert {
        language.language_code
        for language
        in SUPPORTED_LANGUAGES
    } == EXPECTED


def test_language_normalization() -> None:
    assert (
        get_language_identity(
            "ta_IN"
        ).language_code
        == "ta-IN"
    )


def test_semantic_voice_has_nine_localizations() -> None:
    assert {
        voice.language_code
        for voice
        in STUDIO_VOICE_01_LOCALIZATIONS
    } == EXPECTED


def test_tamil_runtime_voice_resolves() -> None:
    voice = (
        get_localized_voice_identity(
            "studio_voice_01",
            "ta-IN",
        )
    )

    assert voice is not None

    assert (
        voice.production_voice_id
        == "studio_voice_01_ta"
    )
