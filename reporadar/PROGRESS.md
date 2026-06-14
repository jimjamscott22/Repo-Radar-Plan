# RepoRadar — Progress Log

## Status: MVP Scaffold Complete

---

## What Was Built (v0.1 Scaffold)

### Project Structure

The full package layout from the implementation plan is in place:

```text
reporadar/
├── app.py
├── core/
│   ├── models.py, rg_runner.py, result_parser.py
│   ├── editor.py, presets.py, settings.py
├── ui/
│   ├── main_window.py, results_view.py
│   ├── preview_pane.py, search_worker.py
├── config/settings.json
├── tests/
│   ├── test_result_parser.py, test_rg_runner.py
├── README.md, CLAUDE.md, PROGRESS.md
├── requirements.txt, requirements-dev.txt, pyproject.toml
└── run.sh
```

### Core Layer (`core/`)

- **`models.py`** — `SearchResult` and `SearchOptions` frozen/mutable dataclasses.
- **`rg_runner.py`** — Builds the `rg` argument list from `SearchOptions`. Handles ripgrep exit codes correctly (code 1 = no matches, not an error; code 2 = real error). Security-safe: always uses a list of arguments with a `--` separator, never `shell=True`.
- **`result_parser.py`** — Parses `rg --line-number --column --no-heading` output by splitting on `:` at most three times. Handles colons in match text. Returns `None` for blank or malformed lines.
- **`editor.py`** — Opens a result in Cursor (`cursor -g file:line`), VS Code (`code -g file:line`), or the system default (`xdg-open`). Raises `EditorError` with a friendly message if the binary is not found.
- **`presets.py`** — 8 default developer search presets: TODOs, Python prints, JS console logs, FastAPI routes, possible secrets, Markdown headings, Python imports, Java classes.
- **`settings.py`** — Loads and saves user preferences as JSON. Uses `platformdirs` to resolve `~/.config/reporadar/settings.json` in production; falls back to `config/settings.json` in development. Tracks recent folders, last query, editor preference, and all toggle states.

### UI Layer (`ui/`)

- **`search_worker.py`** — `QThread` subclass that runs a search in the background and emits `finished_ok(results, warning)` or `failed(message)`. Keeps the UI responsive during long searches.
- **`results_view.py`** — Sortable `QTableWidget` (File / Line / Column / Match). Line and column columns sort numerically. Double-click and `Enter` both emit `result_activated`. `UserRole` data on each row stores the full `SearchResult` object.
- **`preview_pane.py`** — Read-only monospace `QPlainTextEdit`. Reads the file on selection, shows ±4 lines of context, marks the matching line with `>`. Skips files over 5 MB.
- **`main_window.py`** — Wires everything together. Includes: folder combo with recents, search input (Enter / Ctrl+Enter), preset dropdown, five toggle checkboxes, glob filter, editor selector, match count label, vertical splitter between results and preview. Persists settings on every search and on close. Keyboard shortcuts: `Ctrl+O`, `Ctrl+Enter`, `Ctrl+L`, `Ctrl+R`.

### Tests

- **`test_result_parser.py`** — 6 cases: normal line, colons in match text, empty output, multiple results, invalid/blank lines, blank line skipping.
- **`test_rg_runner.py`** — 10 cases: command shape, each flag, `--` separator for dash-queries, empty query error, missing folder error, real match via temp file, no-match is not an error.

All core logic was validated against the real `rg 15.1.0` binary.

---

## What Is Not Done Yet

These are the remaining phases from the implementation plan, in priority order.

### Near-Term (next session)

1. **Git initialisation** — `git init`, first commit, push to GitHub. Add a `.desktop` launcher file for the Linux app menu.
2. **Install and launch test** — Install PySide6 in a venv and run the GUI end-to-end for the first time. Fix any widget sizing or layout issues found during visual inspection.
3. **`rg --json` parsing (Phase 9)** — Replace the current `split(":", 3)` parser with structured JSON output for more reliable results, especially for unusual file names. The spec calls this out as a Phase 9 upgrade. Requires updating `rg_runner.py`, `result_parser.py`, and the tests.

### Medium-Term

4. **Custom presets** — UI to create, edit, and delete presets. Saved to `settings.json` under `custom_presets`. The `Preset` dataclass in `presets.py` is already designed to support this.
5. **Result grouping by file** — Optionally display results grouped under their file path (a tree view or collapsible sections) instead of a flat table.
6. **Search history** — Store the last N queries; accessible via a dropdown or `Ctrl+Up`.
7. **Context-line count control** — A spinbox to set the number of surrounding lines shown in the preview pane (currently hardcoded to 4).

### Longer-Term / Stretch

8. **Export results** — Save results as Markdown or JSON from a menu action.
9. **Syntax-highlighted preview** — Use `Pygments` to colour the preview pane. A spec-listed optional dependency.
10. **Multi-repo search** — Select and search across multiple folders at once.
11. **Git-aware search** — Filter results by branch or only search changed files.
12. **Packaging** — AppImage or Flatpak for easy distribution. A `.desktop` file skeleton is already described in the implementation plan.
13. **AI summaries (stretch)** — Summarise search results using a local or remote LLM.
14. **Windows / macOS support** — The code is mostly cross-platform already; needs testing and a `winreg`/`open` path in `editor.py`.

---

## Known Issues / Notes

- The `results_view.py` description in `reporadar_implementation_plan.md` line 122 contains unrelated text (a "DevMon" blurb) that was accidentally pasted in. This has no effect on the code.
- `config/settings.json` is listed in `.gitignore` so personal settings are not committed. The file in the repo is just the blank default template.
- `run.sh` requires the venv to be set up at `.venv/` inside the `reporadar/` directory. Adjust the path if the venv lives elsewhere.
