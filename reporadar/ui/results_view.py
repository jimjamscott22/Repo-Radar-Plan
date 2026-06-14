"""A sortable table widget that displays search results."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)

from ..core.models import SearchResult

_RESULT_ROLE = Qt.ItemDataRole.UserRole


class ResultsView(QTableWidget):
    """Displays ``SearchResult`` rows and emits selection/open signals."""

    result_selected = Signal(object)  # SearchResult
    result_activated = Signal(object)  # SearchResult (double-click / Enter)

    COLUMNS = ("File", "Line", "Column", "Match")

    def __init__(self) -> None:
        super().__init__(0, len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(0, 320)

        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_double_click)

    def set_results(self, results: list[SearchResult]) -> None:
        """Replace all rows with ``results``."""
        self.setSortingEnabled(False)
        self.clearContents()
        self.setRowCount(len(results))

        for row, result in enumerate(results):
            file_item = QTableWidgetItem(result.file_path)
            file_item.setData(_RESULT_ROLE, result)

            line_item = _numeric_item(result.line_number)
            col_item = _numeric_item(result.column_number)
            match_item = QTableWidgetItem(result.line_text.strip())

            self.setItem(row, 0, file_item)
            self.setItem(row, 1, line_item)
            self.setItem(row, 2, col_item)
            self.setItem(row, 3, match_item)

        self.setSortingEnabled(True)

    def clear_results(self) -> None:
        self.clearContents()
        self.setRowCount(0)

    def _selected_result(self) -> SearchResult | None:
        items = self.selectedItems()
        if not items:
            return None
        first = self.item(items[0].row(), 0)
        return first.data(_RESULT_ROLE) if first else None

    def _on_selection_changed(self) -> None:
        result = self._selected_result()
        if result is not None:
            self.result_selected.emit(result)

    def _on_double_click(self, _item: QTableWidgetItem) -> None:
        result = self._selected_result()
        if result is not None:
            self.result_activated.emit(result)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            result = self._selected_result()
            if result is not None:
                self.result_activated.emit(result)
                return
        super().keyPressEvent(event)


def _numeric_item(value: int) -> QTableWidgetItem:
    item = QTableWidgetItem()
    # Store as int so column sorting is numeric, not lexicographic.
    item.setData(Qt.ItemDataRole.DisplayRole, value)
    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    return item
