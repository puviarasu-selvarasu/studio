"""Compile voice performance + WAV timing into trusted acting."""

from __future__ import annotations

from pathlib import Path

from kernel.acting import (
    ActingPoseCue,
    ActingTimeline,
    BlinkCue,
)
from kernel.adapters.audio.wav_lipsync import (
    WavLipSyncAnalyzer,
)
from kernel.voices import (
    VoiceEmotion,
    VoiceEnergy,
    VoicePerformancePlan,
)


class ActingService:
    def __init__(
        self,
        analyzer: WavLipSyncAnalyzer | None = None,
    ) -> None:
        self._analyzer = (
            analyzer
            if analyzer is not None
            else WavLipSyncAnalyzer()
        )

    def compile(
        self,
        performance: VoicePerformancePlan,
        audio_path: Path,
        *,
        fps: int = 24,
        frame_step: int = 2,
    ) -> ActingTimeline:
        analysis = (
            self._analyzer.analyze(
                audio_path,
                fps=fps,
                frame_step=frame_step,
            )
        )

        profile = (
            _emotion_profile(
                performance.emotion
            )
        )

        energy_scale = {
            VoiceEnergy.LOW: 0.72,
            VoiceEnergy.MEDIUM: 1.00,
            VoiceEnergy.HIGH: 1.24,
        }[
            performance.energy
        ]

        end_frame = (
            analysis.end_frame
        )

        accent_frame = max(
            1,
            min(
                end_frame,
                int(
                    round(
                        end_frame
                        * 0.42
                    )
                ),
            ),
        )

        settle_frame = max(
            accent_frame,
            min(
                end_frame,
                int(
                    round(
                        end_frame
                        * 0.78
                    )
                ),
            ),
        )

        accent = ActingPoseCue(
            frame=accent_frame,
            head_pitch_degrees=(
                profile[
                    "head_pitch"
                ]
                * energy_scale
            ),
            head_yaw_degrees=(
                profile[
                    "head_yaw"
                ]
                * energy_scale
            ),
            head_roll_degrees=(
                profile[
                    "head_roll"
                ]
                * energy_scale
            ),
            chest_pitch_degrees=(
                profile[
                    "chest_pitch"
                ]
                * energy_scale
            ),
            brow_left_degrees=(
                profile[
                    "brow_left"
                ]
                * energy_scale
            ),
            brow_right_degrees=(
                profile[
                    "brow_right"
                ]
                * energy_scale
            ),
            eye_open_left=(
                profile[
                    "eye_left"
                ]
            ),
            eye_open_right=(
                profile[
                    "eye_right"
                ]
            ),
            pupil_x=(
                profile[
                    "pupil_x"
                ]
            ),
            pupil_z=(
                profile[
                    "pupil_z"
                ]
            ),
            pupil_scale=(
                profile[
                    "pupil_scale"
                ]
            ),
            mouth_tilt_degrees=(
                profile[
                    "mouth_tilt"
                ]
                * energy_scale
            ),
            mouth_z_offset=(
                profile[
                    "mouth_z"
                ]
            ),
        )

        settle = ActingPoseCue(
            frame=settle_frame,
            head_pitch_degrees=(
                accent.head_pitch_degrees
                * 0.42
            ),
            head_yaw_degrees=(
                accent.head_yaw_degrees
                * -0.30
            ),
            head_roll_degrees=(
                accent.head_roll_degrees
                * 0.30
            ),
            chest_pitch_degrees=(
                accent.chest_pitch_degrees
                * 0.40
            ),
            brow_left_degrees=(
                accent.brow_left_degrees
                * 0.55
            ),
            brow_right_degrees=(
                accent.brow_right_degrees
                * 0.55
            ),
            eye_open_left=(
                1.0
                + (
                    accent.eye_open_left
                    - 1.0
                )
                * 0.55
            ),
            eye_open_right=(
                1.0
                + (
                    accent.eye_open_right
                    - 1.0
                )
                * 0.55
            ),
            pupil_x=(
                accent.pupil_x
                * 0.35
            ),
            pupil_z=(
                accent.pupil_z
                * 0.35
            ),
            pupil_scale=(
                1.0
                + (
                    accent.pupil_scale
                    - 1.0
                )
                * 0.45
            ),
            mouth_tilt_degrees=(
                accent.mouth_tilt_degrees
                * 0.35
            ),
            mouth_z_offset=(
                accent.mouth_z_offset
                * 0.35
            ),
        )

        poses_by_frame = {
            1: ActingPoseCue(
                frame=1,
            ),
            accent_frame: accent,
            settle_frame: settle,
            end_frame: ActingPoseCue(
                frame=end_frame,
            ),
        }

        blink_states: dict[
            int,
            bool,
        ] = {}

        if end_frame >= 10:
            for fraction in (
                0.34,
                0.72,
            ):
                close_frame = max(
                    2,
                    min(
                        end_frame - 1,
                        int(
                            round(
                                end_frame
                                * fraction
                            )
                        ),
                    ),
                )

                open_frame = min(
                    end_frame,
                    close_frame + 2,
                )

                blink_states[
                    close_frame
                ] = True

                blink_states[
                    open_frame
                ] = False

        return ActingTimeline(
            fps=analysis.fps,
            end_frame=end_frame,
            visemes=analysis.visemes,
            blinks=tuple(
                BlinkCue(
                    frame=frame,
                    closed=(
                        blink_states[
                            frame
                        ]
                    ),
                )
                for frame
                in sorted(
                    blink_states
                )
            ),
            poses=tuple(
                poses_by_frame[
                    frame
                ]
                for frame
                in sorted(
                    poses_by_frame
                )
            ),
        )


def _emotion_profile(
    emotion: VoiceEmotion,
) -> dict[
    str,
    float,
]:
    profiles = {
        VoiceEmotion.NEUTRAL: {
            "head_pitch": 0.0,
            "head_yaw": 1.0,
            "head_roll": 0.0,
            "chest_pitch": 0.0,
            "brow_left": 0.0,
            "brow_right": 0.0,
            "eye_left": 0.96,
            "eye_right": 0.96,
            "pupil_x": 0.0,
            "pupil_z": 0.0,
            "pupil_scale": 1.00,
            "mouth_tilt": 0.0,
            "mouth_z": 0.0,
        },

        VoiceEmotion.WARM: {
            "head_pitch": 3.0,
            "head_yaw": 3.5,
            "head_roll": 3.0,
            "chest_pitch": 1.5,
            "brow_left": 3.0,
            "brow_right": -2.0,
            "eye_left": 0.82,
            "eye_right": 0.88,
            "pupil_x": 0.015,
            "pupil_z": 0.010,
            "pupil_scale": 1.05,
            "mouth_tilt": 3.5,
            "mouth_z": 0.012,
        },

        VoiceEmotion.JOYFUL: {
            "head_pitch": 5.0,
            "head_yaw": 5.0,
            "head_roll": 5.0,
            "chest_pitch": 2.5,
            "brow_left": 5.0,
            "brow_right": -5.0,
            "eye_left": 0.62,
            "eye_right": 0.68,
            "pupil_x": 0.018,
            "pupil_z": 0.020,
            "pupil_scale": 1.08,
            "mouth_tilt": 6.0,
            "mouth_z": 0.020,
        },

        VoiceEmotion.SAD: {
            "head_pitch": -7.0,
            "head_yaw": -2.0,
            "head_roll": -3.0,
            "chest_pitch": -4.0,
            "brow_left": -5.0,
            "brow_right": 5.0,
            "eye_left": 0.68,
            "eye_right": 0.63,
            "pupil_x": -0.010,
            "pupil_z": -0.035,
            "pupil_scale": 0.96,
            "mouth_tilt": -5.0,
            "mouth_z": -0.020,
        },

        VoiceEmotion.ANGRY: {
            "head_pitch": -4.0,
            "head_yaw": 4.0,
            "head_roll": 1.0,
            "chest_pitch": 4.0,
            "brow_left": -12.0,
            "brow_right": 12.0,
            "eye_left": 0.48,
            "eye_right": 0.54,
            "pupil_x": 0.0,
            "pupil_z": 0.012,
            "pupil_scale": 0.88,
            "mouth_tilt": -3.0,
            "mouth_z": -0.005,
        },

        VoiceEmotion.FEARFUL: {
            "head_pitch": 7.0,
            "head_yaw": -5.0,
            "head_roll": 4.0,
            "chest_pitch": -3.0,
            "brow_left": 9.0,
            "brow_right": -9.0,
            "eye_left": 1.28,
            "eye_right": 1.22,
            "pupil_x": -0.020,
            "pupil_z": 0.020,
            "pupil_scale": 0.78,
            "mouth_tilt": 2.0,
            "mouth_z": -0.012,
        },

        VoiceEmotion.SERIOUS: {
            "head_pitch": -3.0,
            "head_yaw": 3.0,
            "head_roll": 0.5,
            "chest_pitch": 2.0,
            "brow_left": -8.0,
            "brow_right": 8.0,
            "eye_left": 0.62,
            "eye_right": 0.64,
            "pupil_x": 0.0,
            "pupil_z": 0.010,
            "pupil_scale": 0.92,
            "mouth_tilt": -1.0,
            "mouth_z": 0.0,
        },

        VoiceEmotion.DETERMINED: {
            "head_pitch": -3.0,
            "head_yaw": 4.0,
            "head_roll": 1.5,
            "chest_pitch": 3.0,
            "brow_left": -10.0,
            "brow_right": 10.0,
            "eye_left": 0.56,
            "eye_right": 0.60,
            "pupil_x": 0.012,
            "pupil_z": 0.010,
            "pupil_scale": 0.90,
            "mouth_tilt": 1.0,
            "mouth_z": 0.005,
        },
    }

    return profiles[
        emotion
    ]
