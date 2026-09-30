"""AI Animator application service for Studio."""

from __future__ import annotations

from kernel.animation_ir.models import (
    AnimationScene,
)
from kernel.application.animator_plan import (
    AnimatorPlan,
    AnimatorPlanParseError,
    animation_scene_from_plan,
    animator_plan_from_json,
)
from kernel.capabilities.models import (
    CapabilityRegistry,
)
from kernel.capabilities.validator import (
    CapabilityValidationError,
    validate_animation_capabilities,
)
from kernel.ports.llm import LLMPort


class AnimatorAgentError(Exception):
    """Represent failure to create a trusted animation plan."""


class AnimatorAgent:
    """Convert scene intent into validated Studio Animation IR."""

    def __init__(
        self,
        llm: LLMPort,
        registry: CapabilityRegistry,
    ) -> None:
        """Initialize the Animator Agent."""

        self._llm = llm
        self._registry = registry

    def generate_plan(
        self,
        intent: str,
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
    ) -> AnimatorPlan:
        """Generate and validate an Animator plan from scene intent."""

        if not intent.strip():
            raise ValueError(
                "Animator intent must not be empty."
            )

        if not scene_id.strip():
            raise ValueError(
                "Scene ID must not be empty."
            )

        if not character_id.strip():
            raise ValueError(
                "Character ID must not be empty."
            )

        if duration_seconds <= 0:
            raise ValueError(
                "Scene duration must be greater than zero."
            )

        capability = self._registry.get_character(
            character_id
        )

        if capability is None:
            raise AnimatorAgentError(
                f"Character '{character_id}' is not registered."
            )

        prompt = self._build_prompt(
            intent=intent,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
            supported_actions=capability.actions,
        )

        try:
            raw_json = self._llm.generate(
                prompt,
                system_prompt=self._system_prompt(),
                response_schema=self._response_schema(
                    scene_id=scene_id,
                    character_id=character_id,
                    duration_seconds=duration_seconds,
                    supported_actions=capability.actions,
                ),
            )
        except Exception as exc:
            raise AnimatorAgentError(
                f"Animator LLM generation failed: {exc}"
            ) from exc

        try:
            plan = animator_plan_from_json(
                raw_json
            )
        except AnimatorPlanParseError as exc:
            raise AnimatorAgentError(
                f"Animator returned invalid plan JSON: {exc}"
            ) from exc

        self._validate_request_binding(
            plan,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
        )

        scene = animation_scene_from_plan(
            plan
        )

        try:
            validate_animation_capabilities(
                scene,
                self._registry,
            )
        except CapabilityValidationError as exc:
            raise AnimatorAgentError(
                f"Animator requested unsupported action: {exc}"
            ) from exc

        return plan

    def generate_scene(
        self,
        intent: str,
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
    ) -> AnimationScene:
        """Generate trusted Animation IR from natural-language intent."""

        plan = self.generate_plan(
            intent,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
        )

        return animation_scene_from_plan(
            plan
        )

    @staticmethod
    def _response_schema(
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
        supported_actions: tuple[str, ...],
    ) -> dict[str, object]:
        """Build the constrained JSON Schema supplied to the LLM."""

        schema: dict[str, object] = (
            AnimatorPlan.model_json_schema()
        )

        properties = schema.get(
            "properties"
        )

        if not isinstance(properties, dict):
            raise AnimatorAgentError(
                "AnimatorPlan schema has no properties mapping."
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

        if not isinstance(scene_schema, dict):
            raise AnimatorAgentError(
                "AnimatorPlan scene_id schema is invalid."
            )

        if not isinstance(character_schema, dict):
            raise AnimatorAgentError(
                "AnimatorPlan character_id schema is invalid."
            )

        if not isinstance(duration_schema, dict):
            raise AnimatorAgentError(
                "AnimatorPlan duration schema is invalid."
            )

        scene_schema["const"] = scene_id
        character_schema["const"] = character_id
        duration_schema["const"] = duration_seconds

        definitions = schema.get(
            "$defs"
        )

        if not isinstance(definitions, dict):
            raise AnimatorAgentError(
                "AnimatorPlan schema has no definitions mapping."
            )

        action_definition = definitions.get(
            "AnimatorActionPlan"
        )

        if not isinstance(action_definition, dict):
            raise AnimatorAgentError(
                "Animator action schema definition is missing."
            )

        action_properties = action_definition.get(
            "properties"
        )

        if not isinstance(action_properties, dict):
            raise AnimatorAgentError(
                "Animator action properties are missing."
            )

        action_schema = action_properties.get(
            "action"
        )

        if not isinstance(action_schema, dict):
            raise AnimatorAgentError(
                "Animator action-name schema is missing."
            )

        action_schema["enum"] = list(
            supported_actions
        )

        return schema

    @staticmethod
    def _system_prompt() -> str:
        """Return the fixed Animator-Agent system instruction."""

        return (
            "You are the Studio Animator Agent. "
            "Convert scene intent into a deterministic animation plan. "
            "Return ONLY valid JSON. "
            "Do not use Markdown fences. "
            "Do not include explanations. "
            "Use only the explicitly supported semantic actions. "
            "Never generate Python or Blender code."
        )

    @staticmethod
    def _build_prompt(
        *,
        intent: str,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
        supported_actions: tuple[str, ...],
    ) -> str:
        """Build the constrained Animator planning prompt."""

        actions = ", ".join(
            supported_actions
        )

        return f"""
Create a single-character animation plan.

Scene ID: {scene_id}
Character ID: {character_id}
Scene duration: {duration_seconds} seconds

Scene intent:
{intent}

Supported actions:
{actions}

Return ONLY JSON with exactly this structure:

{{
  "scene_id": "{scene_id}",
  "duration_seconds": {duration_seconds},
  "character_id": "{character_id}",
  "actions": [
    {{
      "action": "supported_action_name",
      "start_seconds": 0.0,
      "duration_seconds": 1.0
    }}
  ]
}}

Rules:
- Use only supported actions listed above.
- Do not invent new actions.
- Use one or more actions.
- All start times must be zero or greater.
- All durations must be greater than zero.
- Every action must finish within the scene duration.
- Keep timing simple and sequential where practical.
- Preserve the requested scene ID exactly.
- Preserve the requested character ID exactly.
- Preserve the requested scene duration exactly.
- Return JSON only.
""".strip()

    @staticmethod
    def _validate_request_binding(
        plan: AnimatorPlan,
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
    ) -> None:
        """Prevent the model from changing trusted request identity."""

        if plan.scene_id != scene_id:
            raise AnimatorAgentError(
                "Animator changed the requested scene ID."
            )

        if plan.character_id != character_id:
            raise AnimatorAgentError(
                "Animator changed the requested character ID."
            )

        if plan.duration_seconds != duration_seconds:
            raise AnimatorAgentError(
                "Animator changed the requested scene duration."
            )