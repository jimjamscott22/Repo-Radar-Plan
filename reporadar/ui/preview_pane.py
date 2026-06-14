"""Shows surrounding source lines for a selected search result."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit

from ..core.models import SearchResult

CONTEXT_LINES = 4
MAX_FILE_BYTES = 5_000_000  # skip reading very large files


class PreviewPane(QPlainTextEdit):
    """A read-only text view that renders context around a match."""

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("monospace"))
        self.setPlaceholderText("Select a result to preview its context.")

    def show_result(self, result: SearchResult) -> None:
        """Load the result's file and display lines around the match."""
        path = Path(result.file_path)
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                self.setPlainText("(File too large to preview.)")
                return
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            self.setPlainText(f"(Could not read file: {exc})")
            return

        match_index = result.line_number - 1
        start = max(0, match_index - CONTEXT_LINES)
        end = min(len(lines), match_index + CONTEXT_LINES + 1)
        width = len(str(end))

        rendered = []
        for i in range(start, end):
            marker = ">" if i == match_index else " "
            rendered.append(f"{marker} {str(i + 1).rjust(width)} | {lines[i]}")

        self.setPlainText("\n".join(rendered))

    def clear_preview(self) -> None:
        self.clear()
