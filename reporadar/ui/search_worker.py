"""Runs ripgrep searches off the GUI thread to keep the UI responsive."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from ..core.models import SearchOptions, SearchResult
from ..core.rg_runner import RipgrepError, run_search


class SearchWorker(QThread):
    """Executes a single search in a background thread.

    Emits exactly one of :attr:`finished_ok` or :attr:`failed` per run.
    """

    finished_ok = Signal(list, str)  # results, warning
    failed = Signal(str)  # error message

    def __init__(self, options: SearchOptions) -> None:
        super().__init__()
        self._options = options

    def run(self) -> None:  # noqa: D401 - QThread entry point
        try:
            results, warning = run_search(self._options)
        except RipgrepError as exc:
            self.failed.emit(str(exc))
            return
        except Exception as exc:  # pragma: no cover - defensive
            self.failed.emit(f"Unexpected error: {exc}")
            return

        typed: list[SearchResult] = results
        self.finished_ok.emit(typed, warning)
