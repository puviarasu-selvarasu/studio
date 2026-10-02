"""Pure language-neutral acting and lip-sync domain."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActingDomainError(
    ValueError
):
    """Raised when trusted acting data is invalid."""


class Viseme(
    str,
    Enum,
):
    """Small language-neutral mouth-shape vocabulary."""

    REST = "rest"
    CLOSED = "closed"
    OPEN = "open"
    WIDE = "wide"
    ROUND = "round"


def _frame(
    value: int,
    *,
    field: str,
) -> int:
    if (
        not isinstance(
            value,
            int,
        )
        or value < 1
    ):
        raise ActingDomainError(
            field
            + " must be an integer >= 1."
        )

    return value


def _bounded(
    value: float,
    *,
    field: str,
    minimum: float,
    maximum: float,
) -> float:
    number = float(
        value
    )

    if not (
        minimum
        <= number
        <= maximum
    ):
        raise ActingDomainError(
            field
            + " must be between "
            + str(
                minimum
            )
            + " and "
            + str(
                maximum
            )
            + "."
        )

    return number


@dataclass(
    frozen=True,
    slots=True,
)
class VisemeCue:
    """One mouth-shape keyframe."""

    frame: int
    viseme: Viseme
    strength: float

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "frame",
            _frame(
                self.frame,
                field="viseme frame",
            ),
        )

        if not isinstance(
            self.viseme,
            Viseme,
        ):
            raise ActingDomainError(
                "viseme must be Viseme."
            )

        object.__setattr__(
            self,
            "strength",
            _bounded(
                self.strength,
                field="viseme strength",
                minimum=0.0,
                maximum=1.0,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class BlinkCue:
    """One eyelid-state keyframe."""

    frame: int
    closed: bool

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "frame",
            _frame(
                self.frame,
                field="blink frame",
            ),
        )

        if not isinstance(
            self.closed,
            bool,
        ):
            raise ActingDomainError(
                "closed must be boolean."
            )


@dataclass(
    frozen=True,
    slots=True,
)
class ActingPoseCue:
    """Small trusted facial/body acting adjustment."""

    frame: int

    head_pitch_degrees: float = 0.0
    head_yaw_degrees: float = 0.0
    head_roll_degrees: float = 0.0

    chest_pitch_degrees: float = 0.0

    brow_left_degrees: float = 0.0
    brow_right_degrees: float = 0.0

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "frame",
            _frame(
                self.frame,
                field="acting pose frame",
            ),
        )

        for field in (
            "head_pitch_degrees",
            "head_yaw_degrees",
            "head_roll_degrees",
            "chest_pitch_degrees",
            "brow_left_degrees",
            "brow_right_degrees",
        ):
            object.__setattr__(
                self,
                field,
                _bounded(
                    getattr(
                        self,
                        field,
                    ),
                    field=field,
                    minimum=-30.0,
                    maximum=30.0,
                ),
            )


@dataclass(
    frozen=True,
    slots=True,
)
class LipSyncAnalysis:
    """CPU-derived mouth timing from one local WAV."""

    fps: int
    end_frame: int
    duration_seconds: float
    visemes: tuple[
        VisemeCue,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.fps,
                int,
            )
            or self.fps <= 0
        ):
            raise ActingDomainError(
                "fps must be a positive integer."
            )

        object.__setattr__(
            self,
            "end_frame",
            _frame(
                self.end_frame,
                field="end_frame",
            ),
        )

        if (
            self.duration_seconds
            <= 0
        ):
            raise ActingDomainError(
                "duration_seconds must be greater than zero."
            )

        if not self.visemes:
            raise ActingDomainError(
                "Lip-sync analysis requires viseme cues."
            )

        _validate_cue_frames(
            self.visemes,
            self.end_frame,
            "visemes",
        )


@dataclass(
    frozen=True,
    slots=True,
)
class ActingTimeline:
    """Trusted language-neutral timeline consumed by Blender."""

    fps: int
    end_frame: int

    visemes: tuple[
        VisemeCue,
        ...,
    ]

    blinks: tuple[
        BlinkCue,
        ...,
    ]

    poses: tuple[
        ActingPoseCue,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if (
            not isinstance(
                self.fps,
                int,
            )
            or self.fps <= 0
        ):
            raise ActingDomainError(
                "fps must be a positive integer."
            )

        object.__setattr__(
            self,
            "end_frame",
            _frame(
                self.end_frame,
                field="end_frame",
            ),
        )

        if not self.visemes:
            raise ActingDomainError(
                "Acting timeline requires viseme cues."
            )

        if not self.poses:
            raise ActingDomainError(
                "Acting timeline requires pose cues."
            )

        _validate_cue_frames(
            self.visemes,
            self.end_frame,
            "visemes",
        )

        _validate_cue_frames(
            self.blinks,
            self.end_frame,
            "blinks",
        )

        _validate_cue_frames(
            self.poses,
            self.end_frame,
            "poses",
        )


def _validate_cue_frames(
    cues: tuple[
        object,
        ...,
    ],
    end_frame: int,
    label: str,
) -> None:
    frames = [
        int(
            getattr(
                cue,
                "frame",
            )
        )
        for cue
        in cues
    ]

    if frames != sorted(
        frames
    ):
        raise ActingDomainError(
            label
            + " must be ordered by frame."
        )

    if (
        len(
            frames
        )
        != len(
            set(
                frames
            )
        )
    ):
        raise ActingDomainError(
            label
            + " may not contain duplicate frames."
        )

    if any(
        frame > end_frame
        for frame
        in frames
    ):
        raise ActingDomainError(
            label
            + " cannot extend beyond end_frame."
        )
