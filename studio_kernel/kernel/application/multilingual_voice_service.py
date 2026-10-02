"""Trusted multilingual voice routing."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from kernel.application.voice_actor_agent import (
    VoiceActorAgent,
)
from kernel.application.voice_casting_service import (
    VoiceCastingService,
)
from kernel.application.voice_production_service import (
    VoiceProductionService,
)
from kernel.languages import (
    get_language_identity,
)
from kernel.ports.tts import (
    TTSPort,
)
from kernel.voices.localization import (
    get_localized_voice_identity,
)
from kernel.voices.models import (
    VoicePerformancePlan,
)


class MultilingualVoiceError(
    RuntimeError
):
    pass


@dataclass(
    frozen=True,
    slots=True,
)
class MultilingualVoiceProductionResult:
    performance_path: Path
    language_context_path: Path
    audio_path: Path


class MultilingualVoiceTTSRegistry:
    def __init__(
        self,
        adapters: Mapping[
            str,
            TTSPort,
        ],
    ) -> None:
        if not adapters:
            raise MultilingualVoiceError(
                "Registry must not be empty."
            )

        self._adapters = dict(
            adapters
        )

    def resolve(
        self,
        production_voice_id: str,
    ) -> TTSPort:
        try:
            return self._adapters[
                production_voice_id
            ]
        except KeyError as exc:
            raise MultilingualVoiceError(
                "Missing TTS runtime: "
                + production_voice_id
            ) from exc


class MultilingualVoicePlanningService:
    def __init__(
        self,
        casting: VoiceCastingService,
    ) -> None:
        self._casting = casting

    def plan_line(
        self,
        agent: VoiceActorAgent,
        dialogue: str,
        *,
        scene_id: str,
        character_id: str,
        language_code: str,
        direction: str = "",
    ) -> VoicePerformancePlan:
        language = (
            get_language_identity(
                language_code
            )
        )

        if language is None:
            raise MultilingualVoiceError(
                "Unsupported language: "
                + language_code
            )

        voice_id = (
            self._casting
            .voice_id_for_character(
                character_id
            )
        )

        if (
            get_localized_voice_identity(
                voice_id,
                language.language_code,
            )
            is None
        ):
            raise MultilingualVoiceError(
                "Voice localization missing."
            )

        return agent.generate_plan(
            dialogue,
            scene_id=scene_id,
            character_id=character_id,
            voice_id=voice_id,
            direction=direction,
            performance_language_code=(
                language.language_code
            ),
        )


class MultilingualVoiceProductionService:
    def __init__(
        self,
        registry: MultilingualVoiceTTSRegistry,
    ) -> None:
        self._registry = registry

    def render(
        self,
        plan: VoicePerformancePlan,
        language_code: str,
        output_directory: Path,
    ) -> MultilingualVoiceProductionResult:
        language = (
            get_language_identity(
                language_code
            )
        )

        if language is None:
            raise MultilingualVoiceError(
                "Unsupported language: "
                + language_code
            )

        localized = (
            get_localized_voice_identity(
                plan.voice_id,
                language.language_code,
            )
        )

        if localized is None:
            raise MultilingualVoiceError(
                "Voice localization missing."
            )

        result = VoiceProductionService(
            self._registry.resolve(
                localized.production_voice_id
            )
        ).render(
            plan,
            output_directory,
        )

        context_path = (
            output_directory
            / "language_context.json"
        )

        context_path.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "language_code": (
                        language.language_code
                    ),
                    "language_name": (
                        language.name
                    ),
                    "base_voice_id": (
                        plan.voice_id
                    ),
                    "production_voice_id": (
                        localized.production_voice_id
                    ),
                    "provider_id": (
                        localized.provider_id
                    ),
                },
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        return MultilingualVoiceProductionResult(
            performance_path=(
                result.performance_path
            ),
            language_context_path=(
                context_path
            ),
            audio_path=(
                result.audio_path
            ),
        )
