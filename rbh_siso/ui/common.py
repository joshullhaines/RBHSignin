"""
Shared UI widgets and helpers used across dialogs.

Keeping these in one module reduces circular-import issues
when dialogs reference each other.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)


# Create a global font class (kept as-is from original file)
Font = QFont()
Font.setPointSize(20)


class WarningDialog(QDialog):
    """
    A generic warning/notification dialog with an optional
    auto-close timer.

    Args:
        WarnMessage: The message to display to the user
        timeOut: Seconds before auto-closing (0 or less = no
                 auto-close)
        parent: Parent widget (optional)
    """

    def __init__(self, WarnMessage, timeOut, parent=None):
        super().__init__(parent)

        self.setWindowTitle("")
        self.hoursMisMatch = QLabel(WarnMessage)
        self.hoursMisMatch.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.hoursMisMatch.setFont(Font)
        self.hoursMisMatch.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        # Acknowledge button
        self.AckBtn = QPushButton(
            text="Acknowledge",
            parent=self,
        )
        self.AckBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.AckBtn.setFont(Font)
        self.AckBtn.clicked.connect(self.Ack)

        self.HourMisMatchLayout = QVBoxLayout()
        self.HourMisMatchLayout.addWidget(
            self.hoursMisMatch, stretch=4,
        )
        self.HourMisMatchLayout.addWidget(
            self.AckBtn, stretch=1,
        )

        self.setLayout(self.HourMisMatchLayout)

        # Auto-close after timeout (ms for QTimer)
        if timeOut > 0:
            QTimer.singleShot(
                int(timeOut * 1000), self.accept,
            )

    def Ack(self):
        """Exit dialog."""
        self.accept()


class InformationInput(QWidget):
    """A generic text prompt with editable text box."""

    def __init__(self, text, parent=None):
        self.text = text
        super().__init__(parent)

        # InputBox
        self.prompt = QLabel(self.text, parent)
        self.prompt.setFont(Font)
        self.prompt.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.prompt.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )
        self.input = QLineEdit(parent)
        self.input.setFont(Font)
        self.input.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.prompt, stretch=2)
        self.layout.addWidget(self.input, stretch=5)
        self.setLayout(self.layout)
