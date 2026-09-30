"""Qt application bootstrap for Studio."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from .main_window import StudioMainWindow


def run(argv: Sequence[str] | None = None) -> int:
    """Launch the Studio desktop application."""

    qt_argv = list(argv) if argv is not None else sys.argv

    app = QApplication.instance()
    owns_app = app is None

    if app is None:
        app = QApplication(qt_argv)

    window = StudioMainWindow()
    window.show()

    if not owns_app:
        return 0

    return app.exec()