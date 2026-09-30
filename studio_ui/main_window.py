"""Main desktop window for Studio."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class StudioMainWindow(QMainWindow):
    """Minimal desktop shell for Studio."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Studio")
        self.resize(1100, 700)

        self.scene_input = QTextEdit()
        self.scene_input.setObjectName("sceneInput")
        self.scene_input.setPlaceholderText(
            "Describe the scene, shot, performance, or story intent..."
        )

        self.direct_button = QPushButton("Direct")
        self.direct_button.setObjectName("directButton")

        self.animate_button = QPushButton("Animate")
        self.animate_button.setObjectName("animateButton")

        self.preview_label = QLabel(
            "Preview\n\nNo rendered shot available yet."
        )
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(420, 320)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")

        self._build_layout()
        self._connect_signals()

    def _build_layout(self) -> None:
        """Build the initial Studio workspace."""

        input_title = QLabel("SCENE / STORY")
        preview_title = QLabel("PREVIEW")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.direct_button)
        button_layout.addWidget(self.animate_button)

        input_layout = QVBoxLayout()
        input_layout.addWidget(input_title)
        input_layout.addWidget(self.scene_input)
        input_layout.addLayout(button_layout)

        input_panel = QWidget()
        input_panel.setLayout(input_layout)

        preview_layout = QVBoxLayout()
        preview_layout.addWidget(preview_title)
        preview_layout.addWidget(self.preview_label)

        preview_panel = QWidget()
        preview_panel.setLayout(preview_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(input_panel)
        splitter.addWidget(preview_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        root_layout = QVBoxLayout()
        root_layout.addWidget(splitter)
        root_layout.addWidget(self.status_label)

        root = QWidget()
        root.setLayout(root_layout)

        self.setCentralWidget(root)

    def _connect_signals(self) -> None:
        """Connect UI controls to temporary shell behavior."""

        self.direct_button.clicked.connect(self._on_direct_clicked)
        self.animate_button.clicked.connect(self._on_animate_clicked)

    def _has_scene_input(self) -> bool:
        """Return whether the creator supplied non-empty scene input."""

        return bool(self.scene_input.toPlainText().strip())

    def _on_direct_clicked(self) -> None:
        """Handle Direct until the Director application service exists."""

        if not self._has_scene_input():
            self.status_label.setText(
                "Enter scene or story intent before directing."
            )
            return

        self.status_label.setText(
            "Director is not connected yet. Scene intent is ready."
        )

    def _on_animate_clicked(self) -> None:
        """Handle Animate until the animation pipeline exists."""

        if not self._has_scene_input():
            self.status_label.setText(
                "Enter scene or story intent before animating."
            )
            return

        self.status_label.setText(
            "Animation pipeline is not connected yet. Scene intent is ready."
        )