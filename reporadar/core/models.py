"""Typed data structures shared across the core and UI layers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """A single ripgrep match."""

    file_path: str
    line_number: int
    column_number: int
    line_text: str


@dataclass
class SearchOptions:
    """User-configured options for a search, mapped to ripgrep flags."""

    query: str
    folder: str
    case_insensitive: bool = False
    whole_word: bool = False
    fixed_string: bool = False
    include_hidden: bool = False
    no_ignore: bool = False
    file_glob: str | None = None
