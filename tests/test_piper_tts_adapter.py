"""Contract tests for Studio's trusted local Piper adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import kernel.adapters.tts.piper as piper_module
from kernel.adapters.tts.piper import (
    PiperTTSAdapter,
    PiperTTSError,
)


def _trusted_files(
    tmp_path: Path,
) -> tuple[
    Path,
    Path,
]:
    executable = (
        tmp_path
        / "piper.exe"
    )

    model = (
        tmp_path
        / "voice.onnx"
    )

    executable.write_bytes(
        b"trusted executable placeholder"
    )

    model.write_bytes(
        b"trusted model placeholder"
    )

    return (
        executable,
        model,
    )


def test_piper_adapter_rejects_blank_text(
    tmp_path: Path,
) -> None:
    executable, model = (
        _trusted_files(
            tmp_path
        )
    )

    adapter = PiperTTSAdapter(
        executable,
        model,
    )

    with pytest.raises(
        ValueError,
        match="blank",
    ):
        adapter.synthesize(
            "   ",
            tmp_path
            / "speech.wav",
        )


def test_piper_adapter_uses_argument_list_and_stdin_without_shell(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable, model = (
        _trusted_files(
            tmp_path
        )
    )

    calls: list[
        tuple[
            list[str],
            str,
            bool,
        ]
    ] = []

    def fake_run(
        command: list[str],
        *,
        input: str,
        capture_output: bool,
        text: bool,
        timeout: float,
        check: bool,
        shell: bool,
    ) -> subprocess.CompletedProcess[str]:
        calls.append(
            (
                command,
                input,
                shell,
            )
        )

        output = Path(
            command[
                command.index(
                    "--output_file"
                )
                + 1
            ]
        )

        output.write_bytes(
            b"RIFF"
            + b"\x00" * 64
        )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        piper_module.subprocess,
        "run",
        fake_run,
    )

    output = (
        tmp_path
        / "speech.wav"
    )

    result = PiperTTSAdapter(
        executable,
        model,
    ).synthesize(
        "Hello from Studio.",
        output,
    )

    assert result == output

    assert calls[0][1] == (
        "Hello from Studio.\n"
    )

    assert calls[0][2] is False

    assert calls[0][0] == [
        str(
            executable
        ),
        "--model",
        str(
            model
        ),
        "--output_file",
        str(
            output
        ),
    ]


def test_piper_adapter_translates_process_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable, model = (
        _trusted_files(
            tmp_path
        )
    )

    def fake_run(
        *args: object,
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="synthetic failure",
        )

    monkeypatch.setattr(
        piper_module.subprocess,
        "run",
        fake_run,
    )

    with pytest.raises(
        PiperTTSError,
        match="synthetic failure",
    ):
        PiperTTSAdapter(
            executable,
            model,
        ).synthesize(
            "Hello.",
            tmp_path
            / "speech.wav",
        )


def test_piper_adapter_rejects_untrusted_missing_model(
    tmp_path: Path,
) -> None:
    executable = (
        tmp_path
        / "piper.exe"
    )

    executable.write_bytes(
        b"placeholder"
    )

    adapter = PiperTTSAdapter(
        executable,
        tmp_path
        / "missing.onnx",
    )

    with pytest.raises(
        PiperTTSError,
        match="voice model",
    ):
        adapter.synthesize(
            "Hello.",
            tmp_path
            / "speech.wav",
        )


def test_piper_adapter_supports_trusted_multi_speaker_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executable, model = (
        _trusted_files(
            tmp_path
        )
    )

    commands: list[
        list[str]
    ] = []

    def fake_run(
        command: list[str],
        *,
        input: str,
        capture_output: bool,
        text: bool,
        timeout: float,
        check: bool,
        shell: bool,
    ) -> subprocess.CompletedProcess[str]:
        del input
        del capture_output
        del text
        del timeout
        del check

        assert shell is False

        commands.append(
            command
        )

        output = Path(
            command[
                command.index(
                    "--output_file"
                )
                + 1
            ]
        )

        output.write_bytes(
            b"RIFF"
            + b"\x00" * 64
        )

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        piper_module.subprocess,
        "run",
        fake_run,
    )

    output = (
        tmp_path
        / "speaker.wav"
    )

    PiperTTSAdapter(
        executable,
        model,
        speaker_id=7,
    ).synthesize(
        "Character voice.",
        output,
    )

    assert "--speaker" in (
        commands[0]
    )

    index = commands[0].index(
        "--speaker"
    )

    assert (
        commands[0][
            index + 1
        ]
        == "7"
    )


def test_piper_adapter_rejects_negative_speaker_id(
    tmp_path: Path,
) -> None:
    executable, model = (
        _trusted_files(
            tmp_path
        )
    )

    with pytest.raises(
        ValueError,
        match="speaker_id",
    ):
        PiperTTSAdapter(
            executable,
            model,
            speaker_id=-1,
        )
