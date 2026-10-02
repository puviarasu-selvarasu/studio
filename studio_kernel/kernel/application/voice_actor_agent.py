"""AI Voice Actor Agent.

The model decides bounded semantic acting intent only.
It never receives filesystem paths, executable paths, shell commands,
or arbitrary audio-engine controls.
"""

from __future__ import annotations

from kernel.ports.llm import (
    LLMPort,
)
from kernel.voices import (
    VoicePerformanceParseError,
    VoicePerformancePlan,
    get_voice_identity,
    voice_performance_plan_from_json,
)


class VoiceActorAgentError(
    RuntimeError
):
    """Raised when AI voice planning cannot produce trusted intent."""


VOICE_PERFORMANCE_RESPONSE_SCHEMA: dict[
    str,
    object,
] = {
    "type": "object",
    "properties": {
        "scene_id": {
            "type": "string",
        },
        "character_id": {
            "type": "string",
        },
        "voice_id": {
            "type": "string",
        },
        "dialogue": {
            "type": "string",
        },
        "emotion": {
            "type": "string",
            "enum": [
                "neutral",
                "warm",
                "joyful",
                "sad",
                "angry",
                "fearful",
                "serious",
                "determined",
            ],
        },
        "energy": {
            "type": "string",
            "enum": [
                "low",
                "medium",
                "high",
            ],
        },
        "pace": {
            "type": "string",
            "enum": [
                "slow",
                "natural",
                "fast",
            ],
        },
        "delivery_note": {
            "type": "string",
        },
    },
    "required": [
        "scene_id",
        "character_id",
        "voice_id",
        "dialogue",
        "emotion",
        "energy",
        "pace",
        "delivery_note",
    ],
    "additionalProperties": False,
}


_SYSTEM_PROMPT = """
You are Studio's Voice Actor Agent.

Your job is to decide HOW an already-written line should be performed.

You may choose only:
- emotion
- energy
- pace
- one short delivery_note

You must preserve exactly:
- scene_id
- character_id
- voice_id
- dialogue

Never rewrite, translate, extend, censor, shorten, or paraphrase dialogue.
Never emit shell commands.
Never emit Python.
Never emit audio-engine commands.
Never emit filesystem paths.
Return JSON only.
""".strip()


class VoiceActorAgent:
    """Plan bounded semantic voice performance through an LLM port."""

    def __init__(
        self,
        llm: LLMPort,
    ) -> None:
        self._llm = llm

    def generate_plan(
        self,
        dialogue: str,
        *,
        scene_id: str,
        character_id: str,
        voice_id: str,
        direction: str = "",
    ) -> VoicePerformancePlan:
        """Generate and validate one voice-performance plan."""

        normalized_dialogue = (
            dialogue.strip()
        )

        normalized_scene = (
            scene_id.strip()
        )

        normalized_character = (
            character_id.strip()
        )

        normalized_voice = (
            voice_id.strip()
        )

        normalized_direction = (
            direction.strip()
        )

        if not normalized_dialogue:
            raise ValueError(
                "dialogue must not be blank."
            )

        if not normalized_scene:
            raise ValueError(
                "scene_id must not be blank."
            )

        if not normalized_character:
            raise ValueError(
                "character_id must not be blank."
            )

        if not normalized_voice:
            raise ValueError(
                "voice_id must not be blank."
            )

        identity = get_voice_identity(
            normalized_voice
        )

        if identity is None:
            raise VoiceActorAgentError(
                "Unknown voice identity: "
                + normalized_voice
            )

        traits = ", ".join(
            identity.traits
        )

        direction_text = (
            normalized_direction
            if normalized_direction
            else "No additional direction."
        )

        prompt = f"""
Scene ID: {normalized_scene}
Character ID: {normalized_character}
Voice ID: {normalized_voice}
Voice language: {identity.language_code}
Voice traits: {traits}

Dialogue:
{normalized_dialogue}

Director performance direction:
{direction_text}

Choose exactly one emotion:
neutral, warm, joyful, sad, angry, fearful, serious, determined

Choose exactly one energy:
low, medium, high

Choose exactly one pace:
slow, natural, fast

Return ONLY JSON with exactly these fields:

{{
  "scene_id": "{normalized_scene}",
  "character_id": "{normalized_character}",
  "voice_id": "{normalized_voice}",
  "dialogue": "{normalized_dialogue}",
  "emotion": "neutral",
  "energy": "medium",
  "pace": "natural",
  "delivery_note": "brief acting note"
}}

Rules:
- Preserve scene_id exactly.
- Preserve character_id exactly.
- Preserve voice_id exactly.
- Preserve dialogue exactly.
- Do not add spoken words.
- Do not remove spoken words.
- Do not translate dialogue.
- Do not invent engine parameters.
- JSON only.
""".strip()

        try:
            raw = self._llm.generate(
                prompt,
                system_prompt=(
                    _SYSTEM_PROMPT
                ),
                response_schema=(
                    VOICE_PERFORMANCE_RESPONSE_SCHEMA
                ),
            )
        except Exception as exc:
            raise VoiceActorAgentError(
                "Voice Actor LLM generation failed."
            ) from exc

        try:
            plan = (
                voice_performance_plan_from_json(
                    raw
                )
            )
        except VoicePerformanceParseError as exc:
            raise VoiceActorAgentError(
                "Voice Actor returned invalid performance JSON."
            ) from exc

        self._validate_binding(
            plan,
            scene_id=normalized_scene,
            character_id=(
                normalized_character
            ),
            voice_id=normalized_voice,
            dialogue=normalized_dialogue,
        )

        return plan

    @staticmethod
    def _validate_binding(
        plan: VoicePerformancePlan,
        *,
        scene_id: str,
        character_id: str,
        voice_id: str,
        dialogue: str,
    ) -> None:
        """Prevent the model from changing trusted request identity."""

        if plan.scene_id != scene_id:
            raise VoiceActorAgentError(
                "Voice Actor changed the requested scene ID."
            )

        if (
            plan.character_id
            != character_id
        ):
            raise VoiceActorAgentError(
                "Voice Actor changed the requested character ID."
            )

        if plan.voice_id != voice_id:
            raise VoiceActorAgentError(
                "Voice Actor changed the requested voice ID."
            )

        if plan.dialogue != dialogue:
            raise VoiceActorAgentError(
                "Voice Actor changed the authored dialogue."
            )
