"""RepoRadar application entry point."""

from __future__ import annotations

import sys


def main() -> int:
    # Imported lazily so non-GUI tooling can import the package without PySide6.
    from PySide6.QtWidgets import QApplication

    from reporadar.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("RepoRadar")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
