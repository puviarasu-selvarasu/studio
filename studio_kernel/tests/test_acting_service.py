"""Tests for deterministic voice-performance acting compilation."""

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
        assert audio_path == Path(
            "dialogue.wav"
        )

        assert fps == 24
        assert frame_step == 2

        return LipSyncAnalysis(
            fps=24,
            end_frame=30,
            duration_seconds=1.25,
            visemes=(
                VisemeCue(
                    frame=1,
                    viseme=Viseme.REST,
                    strength=0.0,
                ),
                VisemeCue(
                    frame=7,
                    viseme=Viseme.OPEN,
                    strength=0.6,
                ),
                VisemeCue(
                    frame=30,
                    viseme=Viseme.REST,
                    strength=0.0,
                ),
            ),
        )


def _performance(
    emotion: VoiceEmotion,
    energy: VoiceEnergy,
) -> VoicePerformancePlan:
    return VoicePerformancePlan(
        scene_id="scene_acting",
        character_id="momo",
        voice_id="studio_voice_01",
        dialogue="I knew you would come back.",
        emotion=emotion,
        energy=energy,
        pace=VoicePace.NATURAL,
        delivery_note="Restrained determination.",
    )


def test_acting_service_preserves_audio_viseme_timing() -> None:
    timeline = ActingService(
        FakeAnalyzer()
    ).compile(
        _performance(
            VoiceEmotion.DETERMINED,
            VoiceEnergy.MEDIUM,
        ),
        Path(
            "dialogue.wav"
        ),
    )

    assert timeline.end_frame == 30
    assert timeline.fps == 24

    assert (
        timeline.visemes[
            1
        ].viseme
        is Viseme.OPEN
    )


def test_acting_service_adds_blinks_and_emotional_pose() -> None:
    timeline = ActingService(
        FakeAnalyzer()
    ).compile(
        _performance(
            VoiceEmotion.DETERMINED,
            VoiceEnergy.HIGH,
        ),
        Path(
            "dialogue.wav"
        ),
    )

    assert any(
        cue.closed
        for cue
        in timeline.blinks
    )

    assert any(
        abs(
            cue.brow_left_degrees
        )
        > 5.0
        for cue
        in timeline.poses
    )

    assert any(
        abs(
            cue.head_yaw_degrees
        )
        > 3.0
        for cue
        in timeline.poses
    )


def test_acting_service_does_not_require_language() -> None:
    timeline = ActingService(
        FakeAnalyzer()
    ).compile(
        _performance(
            VoiceEmotion.WARM,
            VoiceEnergy.LOW,
        ),
        Path(
            "dialogue.wav"
        ),
    )

    assert timeline.visemes
    assert not hasattr(
        timeline,
        "language_code",
    )
