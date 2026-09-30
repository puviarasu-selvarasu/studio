"""Ollama adapter implementing the Studio LLM port."""

from __future__ import annotations

from typing import Any, Callable

import requests


class LLMAdapterError(Exception):
    """Represent a failure while communicating with an LLM provider."""

    def __init__(self, message: str) -> None:
        """Initialize the adapter error."""
        super().__init__(message)
        self.message = message


HttpPost = Callable[..., Any]


class OllamaAdapter:

    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 120.0,
        http_post: HttpPost = requests.post,
    ) -> None:
        """Initialize the Ollama adapter.

        Args:
            model: Ollama model name to use.
            base_url: Base URL of the local Ollama server.
            timeout_seconds: Maximum time allowed for one generation request.
            http_post: HTTP POST implementation, injectable for testing.
        """
        if not model.strip():
            raise ValueError("Ollama model must not be empty.")

        if timeout_seconds <= 0:
            raise ValueError("Ollama timeout must be greater than zero.")

        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._http_post = http_post

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        response_schema: dict[str, object] | None = None,
    ) -> str:
        """Generate text using the configured Ollama model.

        Args:
            prompt: User/application prompt.
            system_prompt: Optional system instruction.
            response_schema: Optional JSON Schema used to constrain output.

        Returns:
            Generated text.

        Raises:
            LLMAdapterError: If Ollama cannot process the request.
        """
        if not prompt.strip():
            raise ValueError("LLM prompt must not be empty.")

        payload: dict[str, object] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }

        if system_prompt is not None:
            payload["system"] = system_prompt

        if response_schema is not None:
            if not isinstance(response_schema, dict) or not response_schema:
                raise ValueError(
                    "LLM response schema must be a non-empty mapping."
                )

            payload["format"] = response_schema
            payload["options"] = {
                "temperature": 0,
            }

        try:
            response = self._http_post(
                f"{self._base_url}/api/generate",
                json=payload,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise LLMAdapterError(
                f"Ollama request failed: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise LLMAdapterError(
                "Ollama returned an invalid JSON response."
            ) from exc

        if not isinstance(response_data, dict):
            raise LLMAdapterError(
                "Ollama response root must be a JSON object."
            )

        generated_text = response_data.get("response")

        if not isinstance(generated_text, str):
            raise LLMAdapterError(
                "Ollama response does not contain a valid 'response' field."
            )

        return generated_text
