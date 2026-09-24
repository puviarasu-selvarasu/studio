"""Port defining the contract for animation execution."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class AnimatorPort(Protocol):
    """Define the operations required from an animation engine."""

    def animate(
        self,
        animation_ir: dict[str, object],
        output_directory: Path,
    ) -> Path:
        """Execute validated animation instructions.

        Args:
            animation_ir: Validated Animation IR represented as a mapping.
            output_directory: Directory where animation artifacts are written.

        Returns:
            Path to the generated animation artifact.

        Raises:
            Exception: Implementations should translate animation-engine failures
                into application/domain-specific exceptions.
        """
        ...