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
            + str(minimum)
            + " and "
            + str(maximum)
            + "."
        )

    return number


@dataclass(
    frozen=True,
    slots=True,
)
class VisemeCue:
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
    """Facial + upper-body acting pose."""

    frame: int

    head_pitch_degrees: float = 0.0
    head_yaw_degrees: float = 0.0
    head_roll_degrees: float = 0.0

    chest_pitch_degrees: float = 0.0

    brow_left_degrees: float = 0.0
    brow_right_degrees: float = 0.0

    eye_open_left: float = 1.0
    eye_open_right: float = 1.0

    pupil_x: float = 0.0
    pupil_z: float = 0.0
    pupil_scale: float = 1.0

    mouth_tilt_degrees: float = 0.0
    mouth_z_offset: float = 0.0

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

        for field in (
            "eye_open_left",
            "eye_open_right",
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
                    minimum=0.10,
                    maximum=1.40,
                ),
            )

        for field in (
            "pupil_x",
            "pupil_z",
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
                    minimum=-0.08,
                    maximum=0.08,
                ),
            )

        object.__setattr__(
            self,
            "pupil_scale",
            _bounded(
                self.pupil_scale,
                field="pupil_scale",
                minimum=0.65,
                maximum=1.35,
            ),
        )

        object.__setattr__(
            self,
            "mouth_tilt_degrees",
            _bounded(
                self.mouth_tilt_degrees,
                field="mouth_tilt_degrees",
                minimum=-15.0,
                maximum=15.0,
            ),
        )

        object.__setattr__(
            self,
            "mouth_z_offset",
            _bounded(
                self.mouth_z_offset,
                field="mouth_z_offset",
                minimum=-0.06,
                maximum=0.06,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LipSyncAnalysis:
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

        if self.duration_seconds <= 0:
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
        len(frames)
        != len(set(frames))
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
