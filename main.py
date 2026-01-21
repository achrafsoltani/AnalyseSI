#!/usr/bin/env python3
"""
AnalyseSI Modern - A MERISE database modeling tool.

Entry point for the application.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from src.views.main_window import MainWindow
from src.utils.constants import APP_NAME
from src.utils.theme import get_stylesheet


def main():
    """Main entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("AnalyseSI")
    app.setDesktopFileName("merisio")

    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app_icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Set application style
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
