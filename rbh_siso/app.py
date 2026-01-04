"""
App entrypoint.

We keep `RBH_volunteersplash.py` as a thin shim for backwards compatibility and packaging.
This module is the single place that starts the Qt event loop.
"""

import sys

from PyQt6.QtWidgets import QApplication

from rbh_siso.ui.main_dialog import RBHSISO


def main() -> None:
	app = QApplication(sys.argv)

	window = RBHSISO()
	window.showMaximized()

	app.exec()


