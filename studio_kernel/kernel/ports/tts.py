"""Port defining the contract for text-to-speech providers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class TTSPort(Protocol):
    """Define the operations required from a text-to-speech provider."""

    def synthesize(
        self,
        text: str,
        output_path: Path,
    ) -> Path:
        """Synthesize speech and write it to an output file.

        Args:
            text: Text that should be spoken.
            output_path: Destination audio file.

        Returns:
            Path to the generated audio file.

        Raises:
            Exception: Implementations should translate provider-specific failures
                into application/domain-specific exceptions.
        """
        ...