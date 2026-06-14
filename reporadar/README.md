# RepoRadar

RepoRadar is a lightweight desktop GUI for fast codebase search powered by
[ripgrep](https://github.com/BurntSushi/ripgrep). It helps developers search
local repositories, inspect TODOs, find debug statements, locate API routes,
and open matches directly in their editor.

> Pick folder -> type search -> press Search -> view results -> double-click to open in Cursor/VS Code

## Status

MVP scaffold (v0.1). Implements the core search loop:

- Folder picker with recent folders
- Search input with `Enter` / `Ctrl+Enter` to run
- Search options: ignore case, whole word, fixed text, hidden files, ignore `.gitignore`
- File extension / glob filter
- Sortable results table (file, line, column, match)
- Preview pane showing context around the selected match
- Editor integration (Cursor, VS Code, or system default)
- Developer search presets (TODOs, prints, console logs, routes, secrets, etc.)
- Settings persisted to JSON
- Non-blocking searches via a background worker thread

## Requirements

- Python 3.11+
- [`ripgrep`](https://github.com/BurntSushi/ripgrep) installed and available as `rg`
- PySide6 (installed via `requirements.txt`)

## Setup

```bash
cd reporadar
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
# from the project root (the directory containing the `reporadar/` package)
python -m reporadar.app
```

or use the launcher script:

```bash
./reporadar/run.sh
```

## Project Structure

```text
reporadar/
├── app.py              # Application entry point
├── core/
│   ├── models.py       # SearchResult / SearchOptions dataclasses
│   ├── rg_runner.py    # Builds & runs ripgrep commands
│   ├── result_parser.py# Parses rg output into structured results
│   ├── editor.py       # Opens results in the preferred editor
│   ├── presets.py      # Default developer search presets
│   └── settings.py     # JSON-backed user preferences
├── ui/
│   ├── main_window.py  # Main layout + event wiring
│   ├── results_view.py # Sortable results table
│   ├── preview_pane.py # Context preview
│   └── search_worker.py# Background search thread
├── config/settings.json
├── tests/              # Unit tests for the core (non-GUI) logic
├── requirements.txt
└── pyproject.toml
```

The GUI layer never calls `rg` directly; it builds a `SearchOptions` and hands
it to the core layer. This keeps the search logic testable in isolation.

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Choose folder |
| `Ctrl+Enter` | Run search |
| `Ctrl+L` | Focus search box |
| `Ctrl+R` | Re-run search |
| `Enter` on result | Open selected result |

## Roadmap

See `../reporadar_implementation_plan.md` for the full phased plan. Next up:
`rg --json` parsing, custom presets, and packaging (`.desktop` launcher / AppImage).
