from kernel.adapters.tts.piper_expression import (
    piper_controls_for_performance,
)
from kernel.voices import (
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformancePlan,
)


def _plan(
    emotion: VoiceEmotion,
) -> VoicePerformancePlan:
    return VoicePerformancePlan(
        scene_id="phase12",
        character_id="momo",
        voice_id="studio_voice_01",
        dialogue="I will not run away again.",
        emotion=emotion,
        energy=VoiceEnergy.MEDIUM,
        pace=VoicePace.NATURAL,
    )


def test_angry_delivery_is_faster_and_louder_than_sad() -> None:
    angry = (
        piper_controls_for_performance(
            _plan(
                VoiceEmotion.ANGRY
            )
        )
    )

    sad = (
        piper_controls_for_performance(
            _plan(
                VoiceEmotion.SAD
            )
        )
    )

    assert (
        angry.length_scale
        < sad.length_scale
    )

    assert (
        angry.volume
        > sad.volume
    )


def test_fearful_delivery_has_more_variation_than_serious() -> None:
    fearful = (
        piper_controls_for_performance(
            _plan(
                VoiceEmotion.FEARFUL
            )
        )
    )

    serious = (
        piper_controls_for_performance(
            _plan(
                VoiceEmotion.SERIOUS
            )
        )
    )

    assert (
        fearful.noise_scale
        > serious.noise_scale
    )

    assert (
        fearful.noise_w_scale
        > serious.noise_w_scale
    )


def test_expression_controls_remain_bounded() -> None:
    for emotion in VoiceEmotion:
        controls = (
            piper_controls_for_performance(
                _plan(
                    emotion
                )
            )
        )

        assert (
            0.72
            <= controls.length_scale
            <= 1.35
        )

        assert (
            0.25
            <= controls.noise_scale
            <= 0.90
        )

        assert (
            0.75
            <= controls.volume
            <= 1.25
        )
