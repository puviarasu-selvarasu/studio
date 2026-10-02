"""Application orchestration for multi-character voice production."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from kernel.application.voice_actor_agent import (
    VoiceActorAgent,
)
from kernel.application.voice_production_service import (
    VoiceProductionResult,
    VoiceProductionService,
)
from kernel.ports.tts import (
    TTSPort,
)
from kernel.voices.casting import (
    VoiceCast,
    VoiceCastError,
)
from kernel.voices.catalog import (
    get_voice_identity,
)
from kernel.voices.models import (
    VoicePerformancePlan,
)


class VoiceCastingServiceError(
    RuntimeError
):
    """Raised when voice casting cannot be resolved safely."""


class VoiceCastingService:
    """Resolve characters to persistent voices for one Voice Actor Agent."""

    def __init__(
        self,
        cast: VoiceCast,
    ) -> None:
        self._cast = cast

        for assignment in (
            cast.assignments
        ):
            if (
                get_voice_identity(
                    assignment.voice_id
                )
                is None
            ):
                raise VoiceCastingServiceError(
                    "Voice cast references unknown voice identity: "
                    + assignment.voice_id
                )

    def voice_id_for_character(
        self,
        character_id: str,
    ) -> str:
        """Resolve one character's semantic voice identity."""

        try:
            return (
                self._cast.voice_id_for(
                    character_id
                )
            )
        except VoiceCastError as exc:
            raise VoiceCastingServiceError(
                str(
                    exc
                )
            ) from exc

    def plan_line(
        self,
        agent: VoiceActorAgent,
        dialogue: str,
        *,
        scene_id: str,
        character_id: str,
        direction: str = "",
    ) -> VoicePerformancePlan:
        """Use the same Voice Actor Agent for any cast character."""

        voice_id = (
            self.voice_id_for_character(
                character_id
            )
        )

        return agent.generate_plan(
            dialogue,
            scene_id=scene_id,
            character_id=character_id,
            voice_id=voice_id,
            direction=direction,
        )


class VoiceTTSRegistry:
    """Trusted runtime mapping from semantic voice IDs to TTS engines."""

    def __init__(
        self,
        adapters: Mapping[
            str,
            TTSPort,
        ],
    ) -> None:
        if not adapters:
            raise VoiceCastingServiceError(
                "Voice TTS registry must not be empty."
            )

        normalized: dict[
            str,
            TTSPort,
        ] = {}

        for voice_id, adapter in (
            adapters.items()
        ):
            key = voice_id.strip()

            if not key:
                raise VoiceCastingServiceError(
                    "Voice TTS registry key must not be blank."
                )

            if (
                get_voice_identity(
                    key
                )
                is None
            ):
                raise VoiceCastingServiceError(
                    "Voice TTS registry references unknown voice: "
                    + key
                )

            normalized[
                key
            ] = adapter

        self._adapters = normalized

    def resolve(
        self,
        voice_id: str,
    ) -> TTSPort:
        """Resolve one trusted TTS implementation."""

        normalized = voice_id.strip()

        try:
            return self._adapters[
                normalized
            ]
        except KeyError as exc:
            raise VoiceCastingServiceError(
                "No TTS runtime registered for voice: "
                + normalized
            ) from exc


class MultiVoiceProductionService:
    """Render dialogue with the correct TTS voice for each character."""

    def __init__(
        self,
        casting: VoiceCastingService,
        registry: VoiceTTSRegistry,
    ) -> None:
        self._casting = casting
        self._registry = registry

    def render(
        self,
        plan: VoicePerformancePlan,
        output_directory: Path,
    ) -> VoiceProductionResult:
        """Validate cast continuity then render through the selected TTS."""

        expected_voice = (
            self._casting
            .voice_id_for_character(
                plan.character_id
            )
        )

        if (
            plan.voice_id
            != expected_voice
        ):
            raise VoiceCastingServiceError(
                "Performance plan voice does not match "
                "the character's persistent voice cast."
            )

        tts = (
            self._registry.resolve(
                plan.voice_id
            )
        )

        return VoiceProductionService(
            tts
        ).render(
            plan,
            output_directory,
        )
