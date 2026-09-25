"""Tests for the Ollama LLM adapter."""

from __future__ import annotations

from typing import Any

import pytest

from kernel.adapters.ollama_adapter import LLMAdapterError, OllamaAdapter


class FakeResponse:
    """Minimal HTTP response used by adapter tests."""

    def __init__(
        self,
        payload: object,
        *,
        error: Exception | None = None,
    ) -> None:
        """Initialize the fake response."""
        self._payload = payload
        self._error = error

    def raise_for_status(self) -> None:
        """Raise the configured HTTP error."""
        if self._error is not None:
            raise self._error

    def json(self) -> object:
        """Return the configured JSON payload."""
        return self._payload


def test_generate_sends_expected_ollama_request() -> None:
    """The adapter should construct the expected Ollama request."""
    captured: dict[str, Any] = {}

    def fake_post(url: str, **kwargs: Any) -> FakeResponse:
        """Capture the request and return a valid response."""
        captured["url"] = url
        captured["kwargs"] = kwargs

        return FakeResponse({"response": "STUDIO_OK"})

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    result = adapter.generate(
        "Say hello.",
        system_prompt="Reply briefly.",
    )

    assert result == "STUDIO_OK"
    assert captured["url"] == "http://127.0.0.1:11434/api/generate"
    assert captured["kwargs"]["timeout"] == 120.0
    assert captured["kwargs"]["json"] == {
        "model": "llama3.2:3b",
        "prompt": "Say hello.",
        "stream": False,
        "system": "Reply briefly.",
    }


def test_generate_works_without_system_prompt() -> None:
    """The adapter should omit the system field when it is not supplied."""
    captured: dict[str, Any] = {}

    def fake_post(url: str, **kwargs: Any) -> FakeResponse:
        """Capture the request."""
        captured["kwargs"] = kwargs
        return FakeResponse({"response": "hello"})

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    assert adapter.generate("Say hello.") == "hello"
    assert "system" not in captured["kwargs"]["json"]


def test_empty_prompt_is_rejected() -> None:
    """An empty prompt should fail before making an HTTP request."""
    adapter = OllamaAdapter(model="llama3.2:3b")

    with pytest.raises(ValueError, match="prompt"):
        adapter.generate("   ")


def test_empty_model_is_rejected() -> None:
    """An empty model name should not be accepted."""
    with pytest.raises(ValueError, match="model"):
        OllamaAdapter(model="   ")


def test_http_failure_becomes_adapter_error() -> None:
    """HTTP failures should be translated into LLMAdapterError."""
    import requests

    def fake_post(url: str, **kwargs: Any) -> FakeResponse:
        """Return a response that raises an HTTP error."""
        return FakeResponse(
            {},
            error=requests.ConnectionError("server unavailable"),
        )

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    with pytest.raises(LLMAdapterError, match="Ollama request failed"):
        adapter.generate("Hello")


def test_invalid_response_json_becomes_adapter_error() -> None:
    """Invalid response JSON should become an adapter error."""
    class InvalidJsonResponse(FakeResponse):
        """Response whose JSON body cannot be decoded."""

        def json(self) -> object:
            """Raise the same exception requests uses for invalid JSON."""
            raise ValueError("invalid json")

    def fake_post(url: str, **kwargs: Any) -> InvalidJsonResponse:
        """Return an invalid JSON response."""
        return InvalidJsonResponse({})

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    with pytest.raises(
        LLMAdapterError,
        match="invalid JSON response",
    ):
        adapter.generate("Hello")


def test_missing_response_field_becomes_adapter_error() -> None:
    """A response without generated text should be rejected."""
    def fake_post(url: str, **kwargs: Any) -> FakeResponse:
        """Return a response missing the response field."""
        return FakeResponse({"model": "llama3.2:3b"})

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    with pytest.raises(
        LLMAdapterError,
        match="response.*field",
    ):
        adapter.generate("Hello")

def test_ollama_adapter_satisfies_llm_port() -> None:
    """OllamaAdapter should satisfy the LLMPort contract."""
    from kernel.ports.llm import LLMPort

    adapter: LLMPort = OllamaAdapter(
        model="llama3.2:3b",
        http_post=lambda *args, **kwargs: FakeResponse(
            {"response": "hello"}
        ),
    )

    assert adapter.generate("Hello") == "hello"