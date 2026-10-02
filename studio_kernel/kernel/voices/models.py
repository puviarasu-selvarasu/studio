"""Pure domain contracts for Studio voice performance."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class VoiceDomainError(ValueError):
    """Raised when trusted voice-domain data is invalid."""


class VoiceEmotion(str, Enum):
    """Bounded acting emotions supported by Voice Actor V1."""

    NEUTRAL = "neutral"
    WARM = "warm"
    JOYFUL = "joyful"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SERIOUS = "serious"
    DETERMINED = "determined"


class VoiceEnergy(str, Enum):
    """Bounded performance energy."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VoicePace(str, Enum):
    """Bounded dialogue pacing."""

    SLOW = "slow"
    NATURAL = "natural"
    FAST = "fast"


def _required_text(
    value: str,
    *,
    field: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise VoiceDomainError(
            field
            + " must be text."
        )

    normalized = value.strip()

    if not normalized:
        raise VoiceDomainError(
            field
            + " must not be blank."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class VoiceIdentity:
    """Persistent semantic identity of one reusable voice."""

    voice_id: str
    language_code: str
    traits: tuple[str, ...]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "voice_id",
            _required_text(
                self.voice_id,
                field="voice_id",
            ),
        )

        object.__setattr__(
            self,
            "language_code",
            _required_text(
                self.language_code,
                field="language_code",
            ),
        )

        if not self.traits:
            raise VoiceDomainError(
                "Voice identity requires at least one trait."
            )

        normalized_traits = tuple(
            _required_text(
                trait,
                field="voice trait",
            )
            for trait in self.traits
        )

        if (
            len(
                set(
                    normalized_traits
                )
            )
            != len(
                normalized_traits
            )
        ):
            raise VoiceDomainError(
                "Voice traits must be unique."
            )

        object.__setattr__(
            self,
            "traits",
            normalized_traits,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class VoicePerformancePlan:
    """Validated acting intent for one spoken dialogue line."""

    scene_id: str
    character_id: str
    voice_id: str
    dialogue: str
    emotion: VoiceEmotion
    energy: VoiceEnergy
    pace: VoicePace
    delivery_note: str = ""

    def __post_init__(
        self,
    ) -> None:
        for field in (
            "scene_id",
            "character_id",
            "voice_id",
            "dialogue",
        ):
            object.__setattr__(
                self,
                field,
                _required_text(
                    getattr(
                        self,
                        field,
                    ),
                    field=field,
                ),
            )

        if not isinstance(
            self.emotion,
            VoiceEmotion,
        ):
            raise VoiceDomainError(
                "emotion must be VoiceEmotion."
            )

        if not isinstance(
            self.energy,
            VoiceEnergy,
        ):
            raise VoiceDomainError(
                "energy must be VoiceEnergy."
            )

        if not isinstance(
            self.pace,
            VoicePace,
        ):
            raise VoiceDomainError(
                "pace must be VoicePace."
            )

        if not isinstance(
            self.delivery_note,
            str,
        ):
            raise VoiceDomainError(
                "delivery_note must be text."
            )

        normalized_note = (
            self.delivery_note.strip()
        )

        if len(
            normalized_note
        ) > 280:
            raise VoiceDomainError(
                "delivery_note must not exceed 280 characters."
            )

        object.__setattr__(
            self,
            "delivery_note",
            normalized_note,
        )
