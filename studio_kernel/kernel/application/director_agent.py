"""AI Director application service for Studio."""

from __future__ import annotations

from kernel.application.director_plan import (
    DirectorPlan,
    DirectorPlanParseError,
    director_plan_from_json,
)
from kernel.capabilities.models import (
    CapabilityRegistry,
)
from kernel.characters.catalog import (
    CharacterCatalog,
    DEFAULT_CHARACTER_CATALOG,
)
from kernel.characters.models import (
    CharacterIdentity,
    CharacterVariant,
)
from kernel.ports.llm import LLMPort


class DirectorAgentError(Exception):
    """Represent failure to create a trusted Director plan."""


class DirectorAgent:
    """Convert story intent into validated creative shot direction."""

    def __init__(
        self,
        llm: LLMPort,
        registry: CapabilityRegistry,
        catalog: CharacterCatalog = DEFAULT_CHARACTER_CATALOG,
    ) -> None:
        """Initialize the Director Agent."""

        self._llm = llm
        self._registry = registry
        self._catalog = catalog

    def generate_plan(
        self,
        scene_intent: str,
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
        variant_id: str = "default",
    ) -> DirectorPlan:
        """Generate one validated Director plan."""

        if not scene_intent.strip():
            raise ValueError(
                "Director scene intent must not be empty."
            )

        if not scene_id.strip():
            raise ValueError(
                "Scene ID must not be empty."
            )

        if not character_id.strip():
            raise ValueError(
                "Character ID must not be empty."
            )

        if not variant_id.strip():
            raise ValueError(
                "Variant ID must not be empty."
            )

        if duration_seconds <= 0:
            raise ValueError(
                "Scene duration must be greater than zero."
            )

        capability = self._registry.get_character(
            character_id
        )

        if capability is None:
            raise DirectorAgentError(
                f"Character '{character_id}' is not registered."
            )

        identity = self._catalog.get_identity(
            character_id
        )

        if identity is None:
            raise DirectorAgentError(
                f"Character identity '{character_id}' is not registered."
            )

        variant = self._catalog.get_variant(
            character_id,
            variant_id,
        )

        if variant is None:
            raise DirectorAgentError(
                "Character variant "
                f"'{character_id}:{variant_id}' is not registered."
            )

        prompt = self._build_prompt(
            scene_intent=scene_intent,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
            identity=identity,
            variant=variant,
        )

        try:
            raw_json = self._llm.generate(
                prompt,
                system_prompt=self._system_prompt(),
                response_schema=self._response_schema(
                    scene_id=scene_id,
                    character_id=character_id,
                    duration_seconds=duration_seconds,
                ),
            )
        except Exception as exc:
            raise DirectorAgentError(
                f"Director LLM generation failed: {exc}"
            ) from exc

        try:
            plan = director_plan_from_json(
                raw_json
            )
        except DirectorPlanParseError as exc:
            raise DirectorAgentError(
                f"Director returned invalid plan JSON: {exc}"
            ) from exc

        self._validate_request_binding(
            plan,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
        )

        return plan

    @staticmethod
    def _response_schema(
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
    ) -> dict[str, object]:
        """Build the request-bound JSON Schema for the Director."""

        schema: dict[str, object] = (
            DirectorPlan.model_json_schema()
        )

        properties = schema.get(
            "properties"
        )

        if not isinstance(
            properties,
            dict,
        ):
            raise DirectorAgentError(
                "DirectorPlan schema has no properties mapping."
            )

        scene_schema = properties.get(
            "scene_id"
        )

        character_schema = properties.get(
            "character_id"
        )

        duration_schema = properties.get(
            "duration_seconds"
        )

        if not isinstance(
            scene_schema,
            dict,
        ):
            raise DirectorAgentError(
                "DirectorPlan scene_id schema is invalid."
            )

        if not isinstance(
            character_schema,
            dict,
        ):
            raise DirectorAgentError(
                "DirectorPlan character_id schema is invalid."
            )

        if not isinstance(
            duration_schema,
            dict,
        ):
            raise DirectorAgentError(
                "DirectorPlan duration schema is invalid."
            )

        scene_schema["const"] = scene_id
        character_schema["const"] = character_id
        duration_schema["const"] = duration_seconds

        return schema

    @staticmethod
    def _system_prompt() -> str:
        """Return the fixed Director-Agent system instruction."""

        return (
            "You are the Studio Director Agent. "
            "Convert scene or story intent into one concise "
            "single-character, single-shot creative direction plan. "
            "Return ONLY valid JSON. "
            "Do not use Markdown fences. "
            "Do not include explanations. "
            "Direct the shot; you are not implementing animation. "
            "Describe performance intent in natural language. "
            "Do not generate semantic animation action names, "
            "frame numbers, Python, Blender code, dialogue, music, "
            "or asset instructions. "
            "Use only framing, camera intent, and pacing values "
            "permitted by the supplied JSON schema."
        )

    @staticmethod
    def _build_prompt(
        *,
        scene_intent: str,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
        identity: CharacterIdentity,
        variant: CharacterVariant,
    ) -> str:
        """Build the constrained Director planning prompt."""

        return f"""
Create one Director plan for a single-character, single-shot scene.

Scene ID: {scene_id}
Character ID: {character_id}
Scene duration: {duration_seconds} seconds

Persistent character identity context:
Display name: {identity.display_name}
Stable appearance: {identity.appearance.summary}
Appearance anchors: {", ".join(identity.appearance.anchors)}
Performance identity: {identity.performance.summary}
Performance traits: {", ".join(identity.performance.traits)}

Selected character variant:
Variant ID: {variant.variant_id}
Variant name: {variant.display_name}
Variant appearance: {variant.appearance.summary}
Variant descriptors: {", ".join(variant.appearance.descriptors)}

Creator scene intent:
{scene_intent}

You are directing the scene, not implementing the animation.

Your responsibilities:
- Identify the scene objective.
- Describe the emotional direction.
- Select one supported framing.
- Select one supported camera intent.
- Select one supported pacing value.
- Describe the character performance intent in natural language.

Supported framing:
- wide
- medium
- close_up

Supported camera intent:
- static
- push_in
- pull_back
- pan_left
- pan_right

Supported pacing:
- slow
- moderate
- fast

Return ONLY JSON with exactly this structure:

{{
  "scene_id": "{scene_id}",
  "duration_seconds": {duration_seconds},
  "character_id": "{character_id}",
  "scene_objective": "creative scene objective",
  "emotion": "emotional direction or progression",
  "shot": {{
    "framing": "supported_framing",
    "camera_intent": "supported_camera_intent",
    "pacing": "supported_pacing"
  }},
  "performance_intent": "natural-language acting direction"
}}

Rules:
- Preserve the requested scene ID exactly.
- Preserve the requested character ID exactly.
- Preserve the requested scene duration exactly.
- Use the persistent character identity context to keep characterization consistent.
- Respect the selected character variant exactly as appearance context.
- Do not invent a new character identity or a different production variant.
- Use only supported shot values.
- Keep scene_objective concise.
- Keep emotion concise.
- Make performance_intent observable and useful to an Animator.
- Do not output low-level animation actions.
- Do not output frame numbers.
- Do not output Python or Blender code.
- Do not add extra fields.
- Return JSON only.
""".strip()

    @staticmethod
    def _validate_request_binding(
        plan: DirectorPlan,
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
    ) -> None:
        """Prevent the model from changing trusted request identity."""

        if plan.scene_id != scene_id:
            raise DirectorAgentError(
                "Director changed the requested scene ID."
            )

        if plan.character_id != character_id:
            raise DirectorAgentError(
                "Director changed the requested character ID."
            )

        if plan.duration_seconds != duration_seconds:
            raise DirectorAgentError(
                "Director changed the requested scene duration."
            )
