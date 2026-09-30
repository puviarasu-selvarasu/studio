"""Smoke tests for the minimal Studio desktop shell."""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from studio_ui.main_window import StudioMainWindow


def _application() -> QApplication:
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_main_window_exposes_initial_workspace() -> None:
    _application()

    window = StudioMainWindow()

    assert window.windowTitle() == "Studio"
    assert window.scene_input.objectName() == "sceneInput"
    assert window.direct_button.text() == "Direct"
    assert window.animate_button.text() == "Animate"
    assert window.status_label.text() == "Ready"


def test_direct_requires_scene_input() -> None:
    _application()

    window = StudioMainWindow()
    window.direct_button.click()

    assert (
        window.status_label.text()
        == "Enter scene or story intent before directing."
    )


def test_direct_acknowledges_scene_input_without_faking_director() -> None:
    _application()

    window = StudioMainWindow()
    window.scene_input.setPlainText("A character waits beside a quiet station.")
    window.direct_button.click()

    assert (
        window.status_label.text()
        == "Director is not connected yet. Scene intent is ready."
    )


def test_animate_requires_scene_input() -> None:
    _application()

    window = StudioMainWindow()
    window.animate_button.click()

    assert (
        window.status_label.text()
        == "Enter scene or story intent before animating."
    )