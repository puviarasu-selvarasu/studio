from __future__ import annotations

from pathlib import Path

from kernel.acting import (
    LipSyncAnalysis,
    Viseme,
    VisemeCue,
)
from kernel.application.acting_service import (
    ActingService,
)
from kernel.voices import (
    VoiceEmotion,
    VoiceEnergy,
    VoicePace,
    VoicePerformancePlan,
)


class FakeAnalyzer:
    def analyze(
        self,
        audio_path: Path,
        *,
        fps: int,
        frame_step: int,
    ) -> LipSyncAnalysis:
        del audio_path
        del frame_step

        return LipSyncAnalysis(
            fps=fps,
            end_frame=36,
            duration_seconds=1.5,
            visemes=(
                VisemeCue(
                    frame=1,
                    viseme=Viseme.REST,
                    strength=0.0,
                ),
                VisemeCue(
                    frame=10,
                    viseme=Viseme.OPEN,
                    strength=0.8,
                ),
                VisemeCue(
                    frame=36,
                    viseme=Viseme.REST,
                    strength=0.0,
                ),
            ),
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


def _accent(
    emotion: VoiceEmotion,
):
    timeline = ActingService(
        FakeAnalyzer()
    ).compile(
        _plan(
            emotion
        ),
        Path(
            "dialogue.wav"
        ),
    )

    return max(
        timeline.poses,
        key=lambda cue: (
            abs(
                cue.brow_left_degrees
            )
            + abs(
                cue.head_yaw_degrees
            )
            + abs(
                1.0
                - cue.eye_open_left
            )
        ),
    )


def test_angry_expression_narrows_eyes() -> None:
    cue = _accent(
        VoiceEmotion.ANGRY
    )

    assert cue.eye_open_left < 0.70
    assert cue.eye_open_right < 0.70


def test_fearful_expression_widens_eyes_and_shrinks_pupils() -> None:
    cue = _accent(
        VoiceEmotion.FEARFUL
    )

    assert cue.eye_open_left > 1.10
    assert cue.eye_open_right > 1.10
    assert cue.pupil_scale < 0.90


def test_sad_expression_looks_down() -> None:
    cue = _accent(
        VoiceEmotion.SAD
    )

    assert cue.pupil_z < 0
    assert cue.head_pitch_degrees < 0


def test_determined_expression_has_focused_brows() -> None:
    cue = _accent(
        VoiceEmotion.DETERMINED
    )

    assert (
        abs(
            cue.brow_left_degrees
        )
        >= 8.0
    )

    assert cue.eye_open_left < 0.70
