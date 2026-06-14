"""Main application window: layout and event wiring.

This module owns the widgets and orchestrates the core layer. It never calls
``rg`` directly; it builds a :class:`SearchOptions` and hands it to the
background :class:`SearchWorker`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..core.editor import EditorError, open_result
from ..core.models import SearchOptions, SearchResult
from ..core.presets import DEFAULT_PRESETS
from ..core.rg_runner import ripgrep_available
from ..core.settings import Settings, load_settings, save_settings
from .preview_pane import PreviewPane
from .results_view import ResultsView
from .search_worker import SearchWorker

EDITOR_CHOICES = [
    ("Cursor", "cursor"),
    ("VS Code", "code"),
    ("System default", "default"),
]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RepoRadar")
        self.resize(900, 650)

        self.settings: Settings = load_settings()
        self._worker: SearchWorker | None = None

        self._build_ui()
        self._build_shortcuts()
        self._apply_settings()

        if not ripgrep_available():
            self.statusBar().showMessage(
                "ripgrep is not installed or not found in PATH."
            )

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)

        # Folder row
        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Folder:"))
        self.folder_combo = QComboBox()
        self.folder_combo.setEditable(True)
        self.folder_combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        folder_row.addWidget(self.folder_combo, stretch=1)
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._choose_folder)
        folder_row.addWidget(self.browse_button)
        root.addLayout(folder_row)

        # Search row
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))
        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText("Enter a query, regex, or text...")
        self.query_edit.returnPressed.connect(self.run_search)
        search_row.addWidget(self.query_edit, stretch=1)
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Presets...", None)
        for preset in DEFAULT_PRESETS:
            self.preset_combo.addItem(preset.name, preset)
        self.preset_combo.currentIndexChanged.connect(self._apply_preset)
        search_row.addWidget(self.preset_combo)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.run_search)
        search_row.addWidget(self.search_button)
        root.addLayout(search_row)

        # Options row
        options_row = QHBoxLayout()
        self.case_check = QCheckBox("Ignore case")
        self.word_check = QCheckBox("Whole word")
        self.fixed_check = QCheckBox("Fixed text")
        self.hidden_check = QCheckBox("Hidden files")
        self.no_ignore_check = QCheckBox("Ignore .gitignore")
        for box in (
            self.case_check,
            self.word_check,
            self.fixed_check,
            self.hidden_check,
            self.no_ignore_check,
        ):
            options_row.addWidget(box)
        options_row.addStretch(1)
        options_row.addWidget(QLabel("Filter:"))
        self.glob_edit = QLineEdit()
        self.glob_edit.setPlaceholderText("*.py")
        self.glob_edit.setMaximumWidth(140)
        self.glob_edit.returnPressed.connect(self.run_search)
        options_row.addWidget(self.glob_edit)
        root.addLayout(options_row)

        # Editor + status row
        editor_row = QHBoxLayout()
        editor_row.addWidget(QLabel("Open in:"))
        self.editor_combo = QComboBox()
        for label, value in EDITOR_CHOICES:
            self.editor_combo.addItem(label, value)
        self.editor_combo.currentIndexChanged.connect(self._save_editor_choice)
        editor_row.addWidget(self.editor_combo)
        editor_row.addStretch(1)
        self.count_label = QLabel("")
        editor_row.addWidget(self.count_label)
        root.addLayout(editor_row)

        # Results + preview splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.results_view = ResultsView()
        self.results_view.result_selected.connect(self._on_result_selected)
        self.results_view.result_activated.connect(self._open_result)
        splitter.addWidget(self.results_view)

        self.preview_pane = PreviewPane()
        splitter.addWidget(self.preview_pane)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, stretch=1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Ready.")

    def _build_shortcuts(self) -> None:
        def add(seq: QKeySequence.StandardKey | str, slot) -> None:
            action = QAction(self)
            action.setShortcut(seq if isinstance(seq, str) else QKeySequence(seq))
            action.triggered.connect(slot)
            self.addAction(action)

        add("Ctrl+O", self._choose_folder)
        add("Ctrl+Return", self.run_search)
        add("Ctrl+L", lambda: (self.query_edit.setFocus(), self.query_edit.selectAll()))
        add("Ctrl+R", self.run_search)

    def _apply_settings(self) -> None:
        s = self.settings
        self.folder_combo.addItems(s.recent_folders)
        if s.last_folder:
            self.folder_combo.setCurrentText(s.last_folder)
        elif not s.recent_folders:
            self.folder_combo.setCurrentText("")
        if s.last_query:
            self.query_edit.setText(s.last_query)
        self.case_check.setChecked(s.case_insensitive)
        self.word_check.setChecked(s.whole_word)
        self.fixed_check.setChecked(s.fixed_string)
        self.hidden_check.setChecked(s.include_hidden)
        self.no_ignore_check.setChecked(s.no_ignore)
        self.glob_edit.setText(s.file_glob)

        index = self.editor_combo.findData(s.preferred_editor)
        if index >= 0:
            self.editor_combo.setCurrentIndex(index)

    # -------------------------------------------------------------- actions
    def _choose_folder(self) -> None:
        start = self.folder_combo.currentText() or str(
            getattr(self, "_last_browse", "")
        )
        folder = QFileDialog.getExistingDirectory(self, "Select project folder", start)
        if folder:
            self.folder_combo.setCurrentText(folder)

    def _apply_preset(self, index: int) -> None:
        preset = self.preset_combo.itemData(index)
        if preset is None:
            return
        self.query_edit.setText(preset.pattern)
        self.fixed_check.setChecked(preset.fixed_string)
        self.statusBar().showMessage(f"Preset: {preset.name} - {preset.description}")

    def _current_options(self) -> SearchOptions:
        return SearchOptions(
            query=self.query_edit.text(),
            folder=self.folder_combo.currentText().strip(),
            case_insensitive=self.case_check.isChecked(),
            whole_word=self.word_check.isChecked(),
            fixed_string=self.fixed_check.isChecked(),
            include_hidden=self.hidden_check.isChecked(),
            no_ignore=self.no_ignore_check.isChecked(),
            file_glob=self.glob_edit.text().strip() or None,
        )

    def run_search(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        options = self._current_options()
        if not options.query.strip():
            self.statusBar().showMessage("Enter a search term first.")
            return
        if not options.folder:
            self.statusBar().showMessage("Choose a folder to search.")
            return

        self.results_view.clear_results()
        self.preview_pane.clear_preview()
        self.count_label.setText("")
        self._set_searching(True)
        self.statusBar().showMessage("Searching...")

        self._worker = SearchWorker(options)
        self._worker.finished_ok.connect(self._on_search_done)
        self._worker.failed.connect(self._on_search_failed)
        self._worker.finished.connect(lambda: self._set_searching(False))
        self._worker.start()

        self._persist_search_state(options)

    def _set_searching(self, busy: bool) -> None:
        self.search_button.setEnabled(not busy)
        self.search_button.setText("Searching..." if busy else "Search")

    def _on_search_done(self, results: list[SearchResult], warning: str) -> None:
        self.results_view.set_results(results)
        self.count_label.setText(f"{len(results)} matches")
        if not results:
            self.statusBar().showMessage("No matches found.")
        elif warning:
            self.statusBar().showMessage(
                "Some files could not be searched due to permissions."
            )
        else:
            self.statusBar().showMessage(f"Found {len(results)} matches.")

    def _on_search_failed(self, message: str) -> None:
        self.count_label.setText("")
        self.statusBar().showMessage(message)

    def _on_result_selected(self, result: SearchResult) -> None:
        self.preview_pane.show_result(result)

    def _open_result(self, result: SearchResult) -> None:
        editor = self.editor_combo.currentData()
        try:
            open_result(
                result.file_path,
                result.line_number,
                editor=editor,
                custom_command=self.settings.custom_editor_command,
            )
        except EditorError as exc:
            QMessageBox.warning(self, "Editor error", str(exc))

    # ------------------------------------------------------------ persistence
    def _save_editor_choice(self) -> None:
        self.settings.preferred_editor = self.editor_combo.currentData()
        save_settings(self.settings)

    def _persist_search_state(self, options: SearchOptions) -> None:
        s = self.settings
        s.add_recent_folder(options.folder)
        s.last_query = options.query
        s.case_insensitive = options.case_insensitive
        s.whole_word = options.whole_word
        s.fixed_string = options.fixed_string
        s.include_hidden = options.include_hidden
        s.no_ignore = options.no_ignore
        s.file_glob = options.file_glob or ""
        save_settings(s)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._worker is not None and self._worker.isRunning():
            self._worker.wait(2000)
        save_settings(self.settings)
        super().closeEvent(event)
