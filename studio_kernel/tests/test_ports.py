"""Tests for Studio kernel port contracts."""

from __future__ import annotations

from pathlib import Path

from kernel.ports.animator import AnimatorPort
from kernel.ports.llm import LLMPort
from kernel.ports.renderer import RendererPort
from kernel.ports.tts import TTSPort


class FakeLLM:
    """Minimal test implementation of LLMPort."""

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
    ) -> str:
        """Return deterministic test output."""
        return f"generated:{prompt}"


class FakeTTS:
    """Minimal test implementation of TTSPort."""

    def synthesize(
        self,
        text: str,
        output_path: Path,
    ) -> Path:
        """Return the requested output path without external work."""
        return output_path


class FakeAnimator:
    """Minimal test implementation of AnimatorPort."""

    def animate(
        self,
        animation_ir: dict[str, object],
        output_directory: Path,
    ) -> Path:
        """Return a deterministic test artifact path."""
        return output_directory / "animation.test"


class FakeRenderer:
    """Minimal test implementation of RendererPort."""

    def render(
        self,
        scene_path: Path,
        output_path: Path,
    ) -> Path:
        """Return the requested render output path."""
        return output_path


def test_llm_port_shape() -> None:
    """Verify a compatible implementation satisfies LLMPort structurally."""
    adapter: LLMPort = FakeLLM()

    assert adapter.generate("hello") == "generated:hello"


def test_tts_port_shape() -> None:
    """Verify a compatible implementation satisfies TTSPort structurally."""
    adapter: TTSPort = FakeTTS()
    output = Path("speech.wav")

    assert adapter.synthesize("hello", output) == output


def test_animator_port_shape() -> None:
    """Verify a compatible implementation satisfies AnimatorPort structurally."""
    adapter: AnimatorPort = FakeAnimator()
    output_directory = Path("output")

    assert adapter.animate({}, output_directory) == (
        output_directory / "animation.test"
    )


def test_renderer_port_shape() -> None:
    """Verify a compatible implementation satisfies RendererPort structurally."""
    adapter: RendererPort = FakeRenderer()
    output = Path("scene.mp4")

    assert adapter.render(Path("scene"), output) == output