# RepoRadar Spec Sheet

## Project Name

**RepoRadar**

## Project Type

Desktop developer utility

## Short Description

RepoRadar is a lightweight GUI wrapper around `ripgrep` that helps developers search local codebases quickly, inspect results, use saved search presets, and open matches directly in their preferred editor.

---

## Problem Statement

`ripgrep` is extremely fast and powerful, but it is command-line driven. Many developers repeatedly run the same search patterns, inspect the same types of results, or switch between terminal output and an editor.

RepoRadar provides a visual interface for common `ripgrep` workflows while preserving the speed and flexibility of the underlying tool.

---

## Target User

Primary user:

- Developer working on local projects
- Linux desktop user
- Student or self-taught builder managing multiple repos
- Someone who likes CLI tools but wants a faster visual workflow for repeated code searches

Secondary users:

- Developers who want saved search presets
- Beginners learning to explore unfamiliar codebases
- Anyone who wants a simple local code search dashboard

---

## Core Value Proposition

RepoRadar turns `ripgrep` into a visual codebase inspection tool.

Instead of remembering and retyping common commands, the user can select a folder, choose a preset or enter a query, view structured results, preview context, and jump directly to the matching line in an editor.

---

## Main User Workflow

```text
1. Open RepoRadar
2. Select a local project folder
3. Enter a search query or choose a preset
4. Configure search options
5. Run the search
6. Review grouped results
7. Click a result to preview context
8. Double-click to open file at line in editor
```

---

## MVP Scope

### MVP Must Include

- Folder picker
- Search box
- Search button
- Result table
- File path display
- Line number display
- Column number display
- Matching line display
- Case-insensitive toggle
- Whole-word toggle
- Fixed-string toggle
- Basic file extension filter
- Open result in VS Code, Cursor, or default editor
- Graceful handling of no matches and basic errors

### MVP Should Not Include Yet

- AI summaries
- Multi-repo indexing
- Git integration
- Syntax highlighting
- Complex theme editor
- Remote searching
- Background daemons
- Cloud sync

The MVP should be small, sharp, and useful.

---

## Primary Features

## 1. Folder Selection

The user can select a local folder or repository to search.

### Requirements

- Browse button opens a folder picker
- Selected folder path is visible
- App remembers recent folders
- App validates that the folder exists

---

## 2. Search Input

The user can enter a search term, regex, or fixed string.

### Requirements

- Text input for query
- Search button
- Pressing `Enter` or `Ctrl+Enter` can trigger search
- Empty queries should show a friendly warning

---

## 3. Search Options

The user can configure common `ripgrep` flags through GUI controls.

| Option | Description | `rg` Flag |
|---|---|---|
| Case-insensitive | Match regardless of letter case | `-i` |
| Whole word | Match full words only | `-w` |
| Fixed string | Treat query as literal text | `-F` |
| Include hidden files | Search hidden files/folders | `--hidden` |
| Ignore `.gitignore` | Search ignored files too | `--no-ignore` |
| File extension filter | Search files like `.py`, `.js`, `.md` | `-g "*.py"` |

---

## 4. Search Results

Results should be shown in a structured list or table.

### Result Fields

| Field | Description |
|---|---|
| File | Relative or absolute file path |
| Line | Matching line number |
| Column | Starting column of match |
| Match | Matching line text |

### Result Behavior

- Results clear before each new search
- Total match count is displayed
- Results can be sorted by file or line number
- Double-click opens result in editor

---

## 5. Editor Integration

RepoRadar should open selected results in the user's preferred editor.

### Supported Editors

| Editor | Command Format |
|---|---|
| VS Code | `code -g file:line` |
| Cursor | `cursor -g file:line` |
| Default Linux app | `xdg-open file` |
| Custom command | User-defined |

### Requirements

- User can choose preferred editor
- If editor command fails, show friendly error
- Opening at exact line is preferred when supported

---

## 6. Search Presets

RepoRadar should include reusable developer-focused search patterns.

### Default Presets

| Preset | Pattern | Purpose |
|---|---|---|
| TODOs | `TODO|FIXME|HACK` | Find unfinished work |
| Python Prints | `print\(` | Find debug prints |
| JS Console Logs | `console\.log` | Find frontend debug logs |
| FastAPI Routes | `@(app|router)\.(get|post|put|delete|patch)` | Locate API endpoints |
| Possible Secrets | `api[_-]?key|secret|token|password` | Find risky strings |
| Markdown Headings | `^#{1,6}\s` | Outline Markdown files |
| Python Imports | `^(import|from)\s` | Find imports |
| Java Classes | `class\s+\w+` | Find Java class declarations |

### Future Preset Features

- Create custom presets
- Edit presets
- Delete presets
- Mark presets as favorites
- Import/export presets

---

## 7. Preview Pane

The preview pane shows surrounding lines for a selected result.

### Requirements

- Display matching line with nearby context
- Show line numbers
- Make matching line visually obvious
- Handle large files safely

Example preview:

```text
39 | def load_config():
40 |     path = Path("settings.json")
41 |
42 |     # TODO: handle missing file
43 |     return json.loads(path.read_text())
44 |
```

---

## 8. Settings

User preferences should be saved locally.

### Suggested Settings

```json
{
  "preferred_editor": "cursor",
  "recent_folders": [],
  "last_folder": null,
  "last_query": null,
  "include_hidden": false,
  "case_insensitive": false,
  "whole_word": false,
  "fixed_string": false,
  "custom_presets": []
}
```

### Storage Format

Use a local JSON file for MVP.

Suggested location during development:

```text
config/settings.json
```

Possible production location later:

```text
~/.config/reporadar/settings.json
```

---

## Technical Requirements

## Runtime Dependencies

- Python 3.11+
- PySide6
- ripgrep installed and available as `rg`

Optional later:

- Pygments for syntax highlighting
- platformdirs for config path handling
- pytest for tests

---

## Suggested `requirements.txt`

```text
PySide6
pytest
platformdirs
```

---

## Ripgrep Command Strategy

### MVP Command Format

```bash
rg --line-number --column --no-heading "QUERY" "FOLDER"
```

### Example

```bash
rg --line-number --column --no-heading "TODO" /home/jamie/projects/deeptutor
```

### Future Command Format

Use JSON output for more reliable parsing:

```bash
rg --json "QUERY" "FOLDER"
```

---

## Data Model

### SearchResult

```python
from dataclasses import dataclass


@dataclass
class SearchResult:
    file_path: str
    line_number: int
    column_number: int
    line_text: str
```

### SearchOptions

```python
from dataclasses import dataclass


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

---

## Non-Functional Requirements

## Performance

- Searches should feel nearly instant for small and medium repositories
- UI should not freeze during long searches
- Long-term goal: run searches in a worker thread

## Reliability

- No crash on no results
- No crash if `rg` exits with code `1` because no matches were found
- Friendly error when `rg` is missing
- Friendly error for invalid folder

## Usability

- Results should be readable
- Search options should be obvious
- Opening files should be fast
- Common presets should require one click

## Portability

Initial target:

- Ubuntu/Linux desktop

Future targets:

- Windows
- macOS

---

## Error Handling Rules

| Error Case | Expected Behavior |
|---|---|
| `rg` missing | Show install/help message |
| No matches | Show `No matches found` |
| Empty query | Ask user to enter a query |
| Folder missing | Ask user to choose a valid folder |
| Permission denied | Show warning but keep valid results |
| Editor command missing | Show editor configuration error |

---

## UI Layout Concept

```text
┌──────────────────────────────────────────────────────────┐
│ RepoRadar                                                │
├──────────────────────────────────────────────────────────┤
│ Folder: /home/jamie/projects/deeptutor        [Browse]   │
│ Search: [TODO                                  ] [Search] │
│ Options: [ ] Ignore Case  [ ] Whole Word  [ ] Fixed Text │
│ Filter:  [.py                                      ]      │
├──────────────────────────────────────────────────────────┤
│ Results: 12 matches                                      │
│                                                          │
│ File                         Line   Column   Match       │
│ deeptutor/app.py              42     13       # TODO...  │
│ deeptutor/api/routes.py       88     5        TODO...    │
├──────────────────────────────────────────────────────────┤
│ Preview                                                  │
│ 40 | ...                                                 │
│ 41 | ...                                                 │
│ 42 | # TODO: clean this up later                         │
│ 43 | ...                                                 │
└──────────────────────────────────────────────────────────┘
```

---

## Suggested Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Choose folder |
| `Ctrl+Enter` | Run search |
| `Ctrl+L` | Focus search box |
| `Ctrl+R` | Re-run search |
| `Enter` on result | Open selected result |
| `Esc` | Clear search focus or close dialogs |

---

## Security Considerations

RepoRadar should be careful when building subprocess commands.

Recommended approach:

- Use a list of command arguments, not a shell string
- Do not use `shell=True`
- Validate folder paths
- Treat user input as an argument, not executable code

Good pattern:

```python
subprocess.run([
    "rg",
    "--line-number",
    "--column",
    "--no-heading",
    query,
    folder,
])
```

Avoid:

```python
subprocess.run(f"rg {query} {folder}", shell=True)
```

---

## Roadmap

## Version 0.1

- Basic GUI
- Folder picker
- Search input
- Result table
- Run `rg`
- Display results

## Version 0.2

- Search options
- File filter
- Better error handling
- Total result count

## Version 0.3

- Editor integration
- Double-click to open result
- Recent folders

## Version 0.4

- Search presets
- Settings saved to JSON
- Improved UI layout

## Version 0.5

- Preview pane
- Result grouping by file
- `rg --json` parsing

## Version 1.0

- Polished UI
- README with screenshots
- Desktop launcher
- Packaged release
- Stable settings
- Custom presets

---

## Future Feature Ideas

- AI-generated search summaries
- Code smell presets
- Secret scanning mode
- Export results as Markdown
- Export results as JSON
- Save project profiles
- Multi-repo workspace search
- Git-aware search filters
- Search result bookmarks
- Syntax-highlighted preview
- Theme customization
- Plugin system for custom scanners

---

## Success Criteria

RepoRadar is successful when it makes this workflow faster and more comfortable than manually typing repeated `rg` commands:

```text
Find important code patterns → inspect context → jump to file → fix or review
```

The first version does not need to be fancy. It needs to be fast, stable, and useful.
