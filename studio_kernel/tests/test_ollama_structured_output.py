"""Tests for schema-constrained Ollama generation."""

from __future__ import annotations

from typing import Any

from kernel.adapters.ollama_adapter import (
    OllamaAdapter,
)


class FakeResponse:
    """Minimal successful HTTP response."""

    def raise_for_status(
        self,
    ) -> None:
        return None

    def json(
        self,
    ) -> dict[str, object]:
        return {
            "response": '{"value":"ok"}',
        }


def test_ollama_forwards_structured_output_schema() -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        json: dict[str, object],
        timeout: float,
    ) -> FakeResponse:
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "value": {
                "type": "string",
            },
        },
        "required": [
            "value",
        ],
        "additionalProperties": False,
    }

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    result = adapter.generate(
        "Return a structured value.",
        system_prompt="Return JSON.",
        response_schema=schema,
    )

    assert result == '{"value":"ok"}'

    payload = captured["json"]

    assert payload["model"] == "llama3.2:3b"
    assert payload["stream"] is False
    assert payload["system"] == "Return JSON."
    assert payload["format"] == schema
    assert payload["options"] == {
        "temperature": 0,
    }


def test_ollama_omits_format_without_schema() -> None:
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        json: dict[str, object],
        timeout: float,
    ) -> FakeResponse:
        captured["json"] = json
        return FakeResponse()

    adapter = OllamaAdapter(
        model="llama3.2:3b",
        http_post=fake_post,
    )

    adapter.generate(
        "Normal generation."
    )

    payload = captured["json"]

    assert "format" not in payload
    assert "options" not in payload