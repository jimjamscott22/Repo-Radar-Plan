# CLAUDE.md

This file provides guidance when working with the RepoRadar codebase.

## Project Overview

RepoRadar is a lightweight desktop GUI application that wraps `ripgrep` (`rg`) for fast local codebase search. Built with Python and PySide6, targeting Linux desktop. See `../reporadar_spec_sheet.md` for the full product spec and `../reporadar_implementation_plan.md` for the phased build plan.

## Running the App

```bash
# From the repo root (the directory containing the reporadar/ package)
python -m venv .venv && source .venv/bin/activate
pip install -r reporadar/requirements.txt
python -m reporadar.app
```

Or with the launcher script:

```bash
./reporadar/run.sh
```

## Development Commands

```bash
# Install dev dependencies
pip install -r reporadar/requirements-dev.txt

# Run tests (must be run from the repo root so reporadar is importable)
pytest

# Single test file
pytest reporadar/tests/test_result_parser.py -v
```

## Project Structure

```text
reporadar/
├── app.py                  # Entry point: python -m reporadar.app
├── core/                   # Pure-Python, no GUI, fully unit-testable
│   ├── models.py           # SearchResult / SearchOptions dataclasses
│   ├── rg_runner.py        # Builds + runs rg commands, RipgrepError
│   ├── result_parser.py    # Parses rg --line-number --column --no-heading output
│   ├── editor.py           # Opens results in Cursor / VS Code / xdg-open / custom
│   ├── presets.py          # Default developer search presets
│   └── settings.py         # JSON-backed user preferences (platformdirs-aware)
├── ui/                     # PySide6 widgets only; never calls rg directly
│   ├── main_window.py      # Main layout, options, keyboard shortcuts, event wiring
│   ├── results_view.py     # Sortable QTableWidget for search results
│   ├── preview_pane.py     # Context preview with match highlight
│   └── search_worker.py    # QThread wrapper so searches don't block the UI
├── config/settings.json    # Default/initial settings (gitignored once personalised)
├── assets/icons/           # App icon placeholder
└── tests/                  # Unit tests for core logic (no GUI required)
```

## Architecture Rules

- **Strict core/UI separation.** The `core/` layer knows nothing about widgets. The `ui/` layer knows nothing about `subprocess`. The UI builds a `SearchOptions` and passes it to `SearchWorker`; results come back via Qt signals.
- **Never use `shell=True`** or string interpolation when building subprocess commands. Always use a list of arguments and the `--` separator so user input cannot be misinterpreted as flags.
- **Settings** live in JSON. During development: `config/settings.json`. In production: `~/.config/reporadar/settings.json` (resolved by `platformdirs`).

## Key Types

```python
@dataclass(frozen=True)
class SearchResult:
    file_path: str
    line_number: int
    column_number: int
    line_text: str

@dataclass
class SearchOptions:
    query: str
    folder: str
    case_insensitive: bool = False
    whole_word: bool = False
    fixed_string: bool = False
    include_hidden: bool = False
    no_ignore: bool = False
    file_glob: str | None = None
```

## Error Handling Conventions

| Situation | Handling |
|---|---|
| `rg` not installed | `RipgrepError` raised in `rg_runner`; shown in status bar |
| Empty query | `RipgrepError` before subprocess is called |
| Missing folder | `RipgrepError` before subprocess is called |
| No matches | `rg` exits with code 1 — this is NOT an error; return empty list |
| Genuine `rg` error | `rg` exits with code 2 — raise `RipgrepError` with stderr |
| Editor not found | `EditorError` raised in `editor.py`; shown in `QMessageBox` |

## Testing Notes

- Tests live in `reporadar/tests/` and test only `core/` (no Qt required).
- Run from the **repo root** (`cd Repo-Radar-Plan && pytest`).
- `test_rg_runner.py` includes an integration test that writes a real temp file and calls `rg`. Requires `rg` to be installed.

## Runtime Requirements

- Python 3.11+
- `ripgrep` (`rg`) installed and on PATH
- PySide6 (Qt 6.6+)
- `platformdirs` (for config path resolution)
