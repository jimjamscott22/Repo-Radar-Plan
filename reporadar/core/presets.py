"""Reusable developer-focused search presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Preset:
    """A named search pattern.

    ``fixed_string`` indicates the pattern should be treated as literal text
    rather than a regular expression.
    """

    name: str
    pattern: str
    description: str = ""
    fixed_string: bool = False


DEFAULT_PRESETS: list[Preset] = [
    Preset("TODOs", r"TODO|FIXME|HACK", "Find unfinished work"),
    Preset("Python Prints", r"print\(", "Find debug prints"),
    Preset("JS Console Logs", r"console\.log", "Find frontend debug logs"),
    Preset(
        "FastAPI Routes",
        r"@(app|router)\.(get|post|put|delete|patch)",
        "Locate API endpoints",
    ),
    Preset(
        "Possible Secrets",
        r"api[_-]?key|secret|token|password",
        "Find risky strings",
    ),
    Preset("Markdown Headings", r"^#{1,6}\s", "Outline Markdown files"),
    Preset("Python Imports", r"^(import|from)\s", "Find imports"),
    Preset("Java Classes", r"class\s+\w+", "Find Java class declarations"),
]
