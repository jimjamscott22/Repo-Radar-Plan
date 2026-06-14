"""Load and save user preferences as a local JSON file.

During development the file lives at ``config/settings.json`` next to the
package. ``platformdirs`` is used (when available) to choose a proper
per-user location, falling back to the bundled config directory.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    from platformdirs import user_config_dir

    _CONFIG_DIR = Path(user_config_dir("reporadar"))
except Exception:  # pragma: no cover - platformdirs optional at runtime
    _CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

SETTINGS_PATH = _CONFIG_DIR / "settings.json"

MAX_RECENT_FOLDERS = 10


@dataclass
class Settings:
    """Persisted user preferences."""

    preferred_editor: str = "cursor"
    custom_editor_command: str = ""
    recent_folders: list[str] = field(default_factory=list)
    last_folder: str | None = None
    last_query: str | None = None
    include_hidden: bool = False
    case_insensitive: bool = False
    whole_word: bool = False
    fixed_string: bool = False
    no_ignore: bool = False
    file_glob: str = ""

    def add_recent_folder(self, folder: str) -> None:
        """Record ``folder`` as the most recently used, de-duplicated."""
        if folder in self.recent_folders:
            self.recent_folders.remove(folder)
        self.recent_folders.insert(0, folder)
        del self.recent_folders[MAX_RECENT_FOLDERS:]
        self.last_folder = folder


def load_settings(path: Path = SETTINGS_PATH) -> Settings:
    """Load settings from ``path``, returning defaults if missing/invalid."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return Settings()

    known = {f for f in Settings.__dataclass_fields__}
    filtered = {k: v for k, v in data.items() if k in known}
    return Settings(**filtered)


def save_settings(settings: Settings, path: Path = SETTINGS_PATH) -> None:
    """Persist ``settings`` to ``path`` as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
