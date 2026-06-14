# RepoRadar Implementation Plan

A practical implementation roadmap for building **RepoRadar**, a personal GUI wrapper around `ripgrep` (`rg`) for fast codebase search, developer presets, and project inspection.

---

## 1. Project Goal

RepoRadar is a lightweight desktop application that lets a user search through local repositories using the speed of `ripgrep`, while providing a friendly GUI for search options, grouped results, file previews, and editor integration.

The first version should focus on being useful, simple, and stable.

Core workflow:

```text
Choose folder → enter search query → run ripgrep → display results → open file at matching line
```

---

## 2. Recommended Tech Stack

### MVP Stack

**Python + PySide6**

Why this stack is a strong starting point:

- Fast to prototype
- Easy to call `rg` using Python's `subprocess`
- Good fit for a Linux desktop utility
- Keeps the first version focused on functionality
- Useful for learning GUI architecture, subprocess management, parsing, and config files

### Future Stack Option

**Tauri + React/TypeScript + Rust**

This could be a polished version after the MVP works well.

Advantages:

- Modern UI
- Lightweight desktop packaging
- Strong portfolio value
- Rust pairs naturally with `ripgrep`

Recommendation:

Build the MVP in Python first. Later, either polish the Python app or rebuild the concept in Tauri.

---

## 3. MVP Feature Set

Version 1 should include only the essential features.

### Required MVP Features

- Folder/repository picker
- Search input box
- Search button
- Result list/table
- Show file path
- Show line number
- Show column number if available
- Show matching line text
- Open matching file in editor
- Basic search toggles:
  - Case-insensitive search
  - Whole-word search
  - Regex mode
  - Fixed-string mode
- Basic file extension filter, such as `.py`, `.js`, `.md`

### Nice-to-Have MVP Features

- Clear results button
- Search status message
- Count of total matches
- Recent folders dropdown
- Keyboard shortcut for search, such as `Ctrl+Enter`
- Keyboard shortcut for clearing results, such as `Ctrl+L`

---

## 4. Suggested Project Structure

```text
reporadar/
├── app.py
├── core/
│   ├── rg_runner.py
│   ├── result_parser.py
│   ├── models.py
│   └── presets.py
├── ui/
│   ├── main_window.py
│   ├── results_view.py
│   └── preview_pane.py
├── config/
│   └── settings.json
├── assets/
│   └── icons/
├── tests/
│   ├── test_result_parser.py
│   └── test_rg_runner.py
├── README.md
└── requirements.txt
```

### File Responsibilities

| File | Purpose |
|---|---|
| `app.py` | Application entry point |
| `core/rg_runner.py` | Builds and runs `rg` commands |
| `core/result_parser.py` | Parses `rg` output into structured results |
| `core/models.py` | Stores result data classes or typed structures |
| `core/presets.py` | Stores reusable search presets |
| `ui/main_window.py` | Main GUI layout and event wiring |
| `ui/results_view.py` | xxxxxxxxxx [{  "pid": 1234,  "name": "node",  "cmd": "next dev",  "cpu": 5.2,  "memory": 120.5,  "port": 3000}]POST /kill/{pid}​Terminates process​GET /system​Returns system-wide stats​{  "cpu_total": 22.5,  "memory_total": 48,  "memory_used": 12.3}🧠 How It WorksBackend scans processes using psutilFilters relevant dev processesExtracts:CommandPIDResource usageMatches process to open portSends data to frontendFrontend updates UI (polling or WebSocket)🔥 Stretch Features🧊 “Idle Detection”Highlight processes using near 0% CPU🧠 Smart suggestions:“This server has been idle for 2 hours. Kill it?”📊 Historical graphs🐳 Docker container monitoring🌐 Tailscale integration (monitor remote dev servers 👀)🔔 Notifications when CPU spikes🚀 MVP PlanPhase 1 (Backend)Set up FastAPIImplement /processes endpointUse psutil to list processesPhase 2 (Frontend)Basic React dashboardDisplay process listPhase 3Add resource stats (CPU, RAM)Add port detectionPhase 4Add kill process button💡 Why This Project is ValuableTeaches system-level programming conceptsUseful daily developer toolGreat portfolio project (very practical)Bridges backend + frontend + OS-level interaction🧪 Future Expansion IdeasIntegrate into your ContextGrid projectAdd AI insights:“Your Next.js dev server is consuming 800MB RAM”​Build CLI companion:devmon listdevmon kill 3000🧙 Final Vision​A clean dashboard where you can instantly see:“Oh… I have 3 dev servers running and one is eating 1GB RAM like it’s at a buffet.”​…and shut it down with one click.json |
| `ui/preview_pane.py` | Shows surrounding context for selected result |
| `config/settings.json` | Stores user preferences |
| `tests/` | Unit tests for non-GUI logic |

---

## 5. Development Phases

## Phase 1: Command-Line Proof of Concept

Goal: prove that Python can run `rg`, capture output, and parse results.

Tasks:

1. Create a Python function that runs `rg`.
2. Use `--line-number`, `--column`, and `--no-heading`.
3. Capture `stdout` and `stderr`.
4. Print results in the terminal.
5. Handle no matches without treating it as a crash.

Suggested command format:

```bash
rg --line-number --column --no-heading "TODO" /path/to/project
```

Python proof-of-concept:

```python
import subprocess
from pathlib import Path


def run_rg(query: str, folder: str) -> str:
    command = [
        "rg",
        "--line-number",
        "--column",
        "--no-heading",
        query,
        folder,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.stdout


if __name__ == "__main__":
    print(run_rg("TODO", "."))
```

Expected output style:

```text
src/app.py:42:13:# TODO: clean this up later
```

---

## Phase 2: Result Parser

Goal: convert raw `rg` lines into structured Python objects.

Each result should become something like:

```python
{
    "file": "src/app.py",
    "line": 42,
    "column": 13,
    "text": "# TODO: clean this up later"
}
```

Suggested model:

```python
from dataclasses import dataclass


@dataclass
class SearchResult:
    file_path: str
    line_number: int
    column_number: int
    line_text: str
```

Parser considerations:

- File paths can contain colons on some systems, especially Windows paths.
- Since the user is currently focused on Linux, simple colon splitting is acceptable for MVP.
- Long term, prefer `rg --json` for reliable structured output.

MVP parser strategy:

```python
parts = line.split(":", 3)
```

This gives:

```text
file_path, line_number, column_number, line_text
```

---

## Phase 3: Basic PySide6 GUI

Goal: create a working window that can search and show results.

Main UI elements:

- Folder picker button
- Folder path display
- Search input box
- Search button
- Results table

Suggested layout:

```text
┌─────────────────────────────────────────────┐
│ RepoRadar                                   │
├─────────────────────────────────────────────┤
│ Folder: [/home/user/project] [Browse...]    │
│ Search: [TODO                    ] [Search] │
├─────────────────────────────────────────────┤
│ File                Line   Column   Match   │
│ src/app.py          42     13       TODO... │
└─────────────────────────────────────────────┘
```

Results table columns:

- File
- Line
- Column
- Match

Important implementation rule:

Keep the GUI code separate from the ripgrep-running logic. The UI should ask the core layer to search. The core layer should not know anything about buttons or tables.

---

## Phase 4: Search Options

Goal: add useful `rg` flags through simple GUI toggles.

| GUI Option | `rg` Flag |
|---|---|
| Case-insensitive | `-i` |
| Whole word | `-w` |
| Fixed string | `-F` |
| Include hidden files | `--hidden` |
| Ignore `.gitignore` | `--no-ignore` |
| Context lines | `-C <number>` |
| File type | `-t py`, `-t js`, etc. |
| Glob filter | `-g "*.py"` |

Recommended MVP toggles:

- Case-insensitive
- Whole-word
- Fixed-string
- Include hidden files
- File extension filter

---

## Phase 5: Editor Integration

Goal: allow users to open a result at the exact line.

### VS Code

```bash
code -g path/to/file.py:42
```

### Cursor

```bash
cursor -g path/to/file.py:42
```

### Default Editor Fallback

Use `xdg-open` on Linux:

```bash
xdg-open path/to/file.py
```

GUI behavior:

- Double-click result to open in configured editor
- Add settings option for preferred editor:
  - VS Code
  - Cursor
  - System default
  - Custom command

---

## Phase 6: Search Presets

Goal: turn RepoRadar from a generic search box into a developer inspection tool.

Suggested presets:

| Preset | Pattern |
|---|---|
| TODOs | `TODO|FIXME|HACK` |
| Python debug prints | `print\(` |
| JavaScript console logs | `console\.log` |
| FastAPI routes | `@(app|router)\.(get|post|put|delete|patch)` |
| Possible secrets | `api[_-]?key|secret|token|password` |
| Markdown headings | `^#{1,6}\s` |
| Python imports | `^(import|from)\s` |
| Java classes | `class\s+\w+` |

Preset UI ideas:

- Dropdown menu
- Sidebar buttons
- Search chips
- Favorite presets

---

## Phase 7: Preview Pane

Goal: show context around a selected result.

Behavior:

- User clicks result
- App loads the file
- App displays several lines around the match
- Matching line is visually emphasized

Preview format:

```text
39 | def example():
40 |     setup()
41 |
42 |     # TODO: clean this up later
43 |     return True
44 |
```

This makes the app feel much more useful than a plain result list.

---

## Phase 8: Settings and Persistence

Goal: remember user preferences.

Store settings in JSON.

Example:

```json
{
  "recent_folders": [
    "/home/jamie/projects/deeptutor"
  ],
  "preferred_editor": "cursor",
  "include_hidden": false,
  "default_case_insensitive": false,
  "saved_presets": []
}
```

Settings to persist:

- Recent folders
- Preferred editor
- Last search query
- Last selected folder
- Default toggles
- Custom presets

---

## Phase 9: Better Parsing with `rg --json`

Goal: replace fragile text parsing with structured JSON output.

Command:

```bash
rg --json "TODO" /path/to/project
```

Advantages:

- More reliable parsing
- Better support for weird file names
- Cleaner integration with GUI models
- Easier to extend later

Recommendation:

Use simple `--line-number --column --no-heading` parsing for MVP. Move to `--json` after the GUI works.

---

## Phase 10: Packaging

Goal: make RepoRadar easy to launch like a normal app.

Linux packaging options:

- Python virtual environment + launcher script
- `.desktop` launcher
- AppImage later
- Flatpak later if the project becomes serious

Minimal launcher script idea:

```bash
#!/usr/bin/env bash
cd /path/to/reporadar
source .venv/bin/activate
python app.py
```

Desktop entry idea:

```ini
[Desktop Entry]
Name=RepoRadar
Comment=Fast GUI code search powered by ripgrep
Exec=/path/to/reporadar/run.sh
Icon=/path/to/reporadar/assets/icons/reporadar.png
Terminal=false
Type=Application
Categories=Development;Utility;
```

---

## 6. Testing Plan

Focus tests on the core logic first.

### Test `result_parser.py`

Test cases:

- Normal result line
- Empty output
- Multiple results
- Result with colons in match text
- Invalid result line

### Test `rg_runner.py`

Test cases:

- Builds basic command correctly
- Adds `-i` when case-insensitive is enabled
- Adds `-w` when whole-word is enabled
- Adds `-F` when fixed-string is enabled
- Handles no matches
- Handles missing `rg` executable gracefully

---

## 7. Error Handling

Handle these cases gracefully:

| Situation | User-Friendly Message |
|---|---|
| `rg` is not installed | `ripgrep is not installed or not found in PATH.` |
| Folder does not exist | `Selected folder does not exist.` |
| Empty query | `Enter a search term first.` |
| No results | `No matches found.` |
| Permission denied | `Some files could not be searched due to permissions.` |
| Editor command missing | `Could not open editor. Check your editor setting.` |

---

## 8. Suggested Milestones

### Milestone 1

Working CLI proof-of-concept.

### Milestone 2

Parser converts raw output into structured search results.

### Milestone 3

Basic GUI can select folder, search, and display results.

### Milestone 4

Double-click opens result in VS Code or Cursor.

### Milestone 5

Search options and presets added.

### Milestone 6

Preview pane added.

### Milestone 7

Settings saved to JSON.

### Milestone 8

Project gets README, screenshots, and `.desktop` launcher.

---

## 9. Stretch Features

These should wait until the MVP feels solid.

- Result grouping by file
- Search history
- Saved repo profiles
- Custom search presets
- Export results as Markdown or JSON
- Dark theme
- Syntax-highlighted preview pane
- Watch mode for repeated searches
- AI summary of code search results
- Project health dashboard
- Search result tagging
- Multi-repo search
- Git branch-aware searching

---

## 10. Portfolio Description

Possible GitHub description:

> RepoRadar is a desktop code-search utility powered by ripgrep. It provides fast repository search, developer-focused presets, grouped results, file previews, and editor integration for quickly inspecting local codebases.

Possible README intro:

```markdown
# RepoRadar

RepoRadar is a lightweight desktop GUI for fast codebase search powered by ripgrep. It helps developers search local repositories, inspect TODOs, find debug statements, locate API routes, and open matches directly in their editor.
```

---

## 11. Best First Build Target

The first useful version should do this:

```text
Pick folder → type search → press Search → view results → double-click to open in Cursor/VS Code
```

Do not overbuild the first version. Once that loop works, everything else becomes a clean upgrade path.
