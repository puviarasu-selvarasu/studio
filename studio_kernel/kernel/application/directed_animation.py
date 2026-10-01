"""Director-to-Animator orchestration for Studio."""

from __future__ import annotations

from dataclasses import dataclass

from kernel.animation_ir.models import (
    AnimationScene,
)
from kernel.application.animator_agent import (
    AnimatorAgent,
)
from kernel.application.animator_plan import (
    AnimatorPlan,
    animation_scene_from_plan,
)
from kernel.application.director_agent import (
    DirectorAgent,
)
from kernel.application.director_plan import (
    DirectorPlan,
)


@dataclass(frozen=True)
class DirectedAnimationResult:
    """Hold one trusted Director-to-Animator production handoff."""

    director_plan: DirectorPlan
    animator_plan: AnimatorPlan
    animation_scene: AnimationScene


class DirectedAnimationService:
    """Orchestrate Director planning followed by Animator planning."""

    def __init__(
        self,
        director: DirectorAgent,
        animator: AnimatorAgent,
    ) -> None:
        """Initialize the directed-animation application service."""

        self._director = director
        self._animator = animator

    def generate(
        self,
        scene_intent: str,
        *,
        scene_id: str,
        character_id: str,
        duration_seconds: float,
    ) -> DirectedAnimationResult:
        """Generate Director direction and trusted Animation IR sequentially."""

        director_plan = self._director.generate_plan(
            scene_intent,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
        )

        animator_intent = self._build_animator_intent(
            director_plan
        )

        animator_plan = self._animator.generate_plan(
            animator_intent,
            scene_id=scene_id,
            character_id=character_id,
            duration_seconds=duration_seconds,
        )

        self._validate_handoff(
            director_plan,
            animator_plan,
        )

        animation_scene = animation_scene_from_plan(
            animator_plan
        )

        return DirectedAnimationResult(
            director_plan=director_plan,
            animator_plan=animator_plan,
            animation_scene=animation_scene,
        )

    @staticmethod
    def _build_animator_intent(
        plan: DirectorPlan,
    ) -> str:
        """Translate Director output into Animator-facing creative context."""

        return (
            f"Scene objective: {plan.scene_objective}\n"
            f"Emotion: {plan.emotion}\n"
            f"Performance direction: {plan.performance_intent}\n"
            f"Shot context: framing={plan.shot.framing}, "
            f"camera_intent={plan.shot.camera_intent}, "
            f"pacing={plan.shot.pacing}.\n"
            "Animate only the character performance using supported "
            "semantic character actions. "
            "Treat framing and camera intent as context only; "
            "do not convert camera direction into character actions."
        )

    @staticmethod
    def _validate_handoff(
        director_plan: DirectorPlan,
        animator_plan: AnimatorPlan,
    ) -> None:
        """Require both AI stages to remain aligned to one trusted request."""

        if animator_plan.scene_id != director_plan.scene_id:
            raise RuntimeError(
                "Director-to-Animator handoff changed scene identity."
            )

        if animator_plan.character_id != director_plan.character_id:
            raise RuntimeError(
                "Director-to-Animator handoff changed character identity."
            )

        if (
            animator_plan.duration_seconds
            != director_plan.duration_seconds
        ):
            raise RuntimeError(
                "Director-to-Animator handoff changed scene duration."
            )
