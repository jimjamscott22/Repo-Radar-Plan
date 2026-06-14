"""Parses raw ``rg --line-number --column --no-heading`` output.

Output lines look like::

    src/app.py:42:13:# TODO: clean this up later

The match text itself may contain colons, so we split at most 3 times. File
paths containing colons (e.g. Windows drive paths) are out of scope for the
MVP, which targets Linux; ``rg --json`` is the long-term upgrade path.
"""

from __future__ import annotations

from .models import SearchResult


def parse_line(line: str) -> SearchResult | None:
    """Parse a single ripgrep output line into a :class:`SearchResult`.

    Returns ``None`` for blank or malformed lines.
    """
    if not line:
        return None

    parts = line.split(":", 3)
    if len(parts) < 4:
        return None

    file_path, line_str, column_str, text = parts
    try:
        line_number = int(line_str)
        column_number = int(column_str)
    except ValueError:
        return None

    return SearchResult(
        file_path=file_path,
        line_number=line_number,
        column_number=column_number,
        line_text=text,
    )


def parse_rg_output(output: str) -> list[SearchResult]:
    """Parse the full stdout of a ripgrep run into search results."""
    results: list[SearchResult] = []
    for raw_line in output.splitlines():
        result = parse_line(raw_line)
        if result is not None:
            results.append(result)
    return results
