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
    """Compile deterministic acting without expanding Animation IR."""

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
        """Compile voice performance intent into facial/body acting."""

        analysis = (
            self._analyzer.analyze(
                audio_path,
                fps=fps,
                frame_step=(
                    frame_step
                ),
            )
        )

        profile = (
            _emotion_profile(
                performance.emotion
            )
        )

        energy_scale = {
            VoiceEnergy.LOW: 0.65,
            VoiceEnergy.MEDIUM: 1.00,
            VoiceEnergy.HIGH: 1.30,
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

        poses_by_frame = {
            1: ActingPoseCue(
                frame=1,
            ),

            accent_frame: ActingPoseCue(
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
            ),

            settle_frame: ActingPoseCue(
                frame=settle_frame,
                head_pitch_degrees=(
                    profile[
                        "head_pitch"
                    ]
                    * energy_scale
                    * 0.40
                ),
                head_yaw_degrees=(
                    profile[
                        "head_yaw"
                    ]
                    * energy_scale
                    * -0.35
                ),
                head_roll_degrees=(
                    profile[
                        "head_roll"
                    ]
                    * energy_scale
                    * 0.25
                ),
                chest_pitch_degrees=(
                    profile[
                        "chest_pitch"
                    ]
                    * energy_scale
                    * 0.35
                ),
                brow_left_degrees=(
                    profile[
                        "brow_left"
                    ]
                    * energy_scale
                    * 0.50
                ),
                brow_right_degrees=(
                    profile[
                        "brow_right"
                    ]
                    * energy_scale
                    * 0.50
                ),
            ),

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
            visemes=(
                analysis.visemes
            ),
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
            "head_pitch": 1.5,
            "head_yaw": 2.0,
            "head_roll": 0.5,
            "chest_pitch": 0.5,
            "brow_left": 0.0,
            "brow_right": 0.0,
        },

        VoiceEmotion.WARM: {
            "head_pitch": 3.0,
            "head_yaw": 3.0,
            "head_roll": 2.0,
            "chest_pitch": 1.5,
            "brow_left": 2.0,
            "brow_right": -2.0,
        },

        VoiceEmotion.JOYFUL: {
            "head_pitch": 4.0,
            "head_yaw": 5.0,
            "head_roll": 3.0,
            "chest_pitch": 2.0,
            "brow_left": 4.0,
            "brow_right": -4.0,
        },

        VoiceEmotion.SAD: {
            "head_pitch": -5.0,
            "head_yaw": 1.0,
            "head_roll": -2.0,
            "chest_pitch": -3.0,
            "brow_left": -5.0,
            "brow_right": 5.0,
        },

        VoiceEmotion.ANGRY: {
            "head_pitch": -3.0,
            "head_yaw": 5.0,
            "head_roll": 0.0,
            "chest_pitch": 3.0,
            "brow_left": -9.0,
            "brow_right": 9.0,
        },

        VoiceEmotion.FEARFUL: {
            "head_pitch": 5.0,
            "head_yaw": -5.0,
            "head_roll": 3.0,
            "chest_pitch": -2.0,
            "brow_left": 7.0,
            "brow_right": -7.0,
        },

        VoiceEmotion.SERIOUS: {
            "head_pitch": -2.0,
            "head_yaw": 3.0,
            "head_roll": 0.5,
            "chest_pitch": 1.5,
            "brow_left": -7.0,
            "brow_right": 7.0,
        },

        VoiceEmotion.DETERMINED: {
            "head_pitch": -2.5,
            "head_yaw": 4.0,
            "head_roll": 1.0,
            "chest_pitch": 2.5,
            "brow_left": -8.0,
            "brow_right": 8.0,
        },
    }

    return profiles[
        emotion
    ]
