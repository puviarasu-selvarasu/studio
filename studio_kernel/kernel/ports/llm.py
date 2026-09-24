"""Port defining the contract for large language model providers."""

from __future__ import annotations

from typing import Protocol


class LLMPort(Protocol):
    """Define the operations required from an LLM provider."""

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: User/application prompt supplied to the model.
            system_prompt: Optional instruction defining model behavior.

        Returns:
            The generated text.

        Raises:
            Exception: Implementations should translate provider-specific failures
                into application/domain-specific exceptions.
        """
        ...