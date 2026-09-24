"""Port defining the contract for rendering and video production."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class RendererPort(Protocol):
    """Define the operations required from a rendering system."""

    def render(
        self,
        scene_path: Path,
        output_path: Path,
    ) -> Path:
        """Render a scene to a video or image sequence.

        Args:
            scene_path: Path to the scene or renderable artifact.
            output_path: Destination for rendered output.

        Returns:
            Path to the rendered artifact.

        Raises:
            Exception: Implementations should translate renderer-specific failures
                into application/domain-specific exceptions.
        """
        ...