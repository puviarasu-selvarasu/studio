"""Pure character-to-voice casting contracts."""

from __future__ import annotations

from dataclasses import dataclass


class VoiceCastError(
    ValueError
):
    """Raised when a character voice cast is invalid."""


def _required(
    value: str,
    *,
    field: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise VoiceCastError(
            field
            + " must be text."
        )

    normalized = value.strip()

    if not normalized:
        raise VoiceCastError(
            field
            + " must not be blank."
        )

    return normalized


@dataclass(
    frozen=True,
    slots=True,
)
class CharacterVoiceAssignment:
    """Bind one character identity to one semantic voice identity."""

    character_id: str
    voice_id: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "character_id",
            _required(
                self.character_id,
                field="character_id",
            ),
        )

        object.__setattr__(
            self,
            "voice_id",
            _required(
                self.voice_id,
                field="voice_id",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class VoiceCast:
    """Immutable voice cast for a project, episode, or scene."""

    assignments: tuple[
        CharacterVoiceAssignment,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        if not self.assignments:
            raise VoiceCastError(
                "Voice cast requires at least one assignment."
            )

        character_ids = [
            assignment.character_id
            for assignment
            in self.assignments
        ]

        if (
            len(
                character_ids
            )
            != len(
                set(
                    character_ids
                )
            )
        ):
            raise VoiceCastError(
                "A character may have only one active voice assignment."
            )

    def voice_id_for(
        self,
        character_id: str,
    ) -> str:
        """Resolve the persistent voice assigned to a character."""

        normalized = _required(
            character_id,
            field="character_id",
        )

        for assignment in self.assignments:
            if (
                assignment.character_id
                == normalized
            ):
                return (
                    assignment.voice_id
                )

        raise VoiceCastError(
            "Character is not present in voice cast: "
            + normalized
        )
