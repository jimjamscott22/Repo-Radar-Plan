"""Builds and runs ``ripgrep`` commands.

This module deliberately knows nothing about the GUI. The UI asks this layer
to perform a search; this layer returns structured results or raises a
:class:`RipgrepError` with a friendly message.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .models import SearchOptions, SearchResult
from .result_parser import parse_rg_output

RG_BINARY = "rg"

# ripgrep exit codes:
#   0 -> matches found
#   1 -> no matches found (NOT an error for us)
#   2 -> an actual error occurred
_RG_NO_MATCH = 1


class RipgrepError(Exception):
    """Raised when ripgrep cannot run or fails for a real reason."""


def ripgrep_available() -> bool:
    """Return True if the ``rg`` executable is found on PATH."""
    return shutil.which(RG_BINARY) is not None


def build_command(options: SearchOptions) -> list[str]:
    """Build the ripgrep argument list from search options.

    User input is always passed as discrete arguments (never via a shell
    string) to avoid command injection.
    """
    command: list[str] = [
        RG_BINARY,
        "--line-number",
        "--column",
        "--no-heading",
        "--color",
        "never",
    ]

    if options.case_insensitive:
        command.append("-i")
    if options.whole_word:
        command.append("-w")
    if options.fixed_string:
        command.append("-F")
    if options.include_hidden:
        command.append("--hidden")
    if options.no_ignore:
        command.append("--no-ignore")
    if options.file_glob:
        command.extend(["-g", options.file_glob])

    # ``--`` ensures a query starting with ``-`` is not treated as a flag.
    command.append("--")
    command.append(options.query)
    command.append(options.folder)
    return command


def run_search(options: SearchOptions) -> tuple[list[SearchResult], str]:
    """Run ripgrep and return ``(results, warning_text)``.

    ``warning_text`` carries non-fatal stderr output (e.g. permission denied
    on some files) so the UI can surface it without discarding valid results.

    Raises:
        RipgrepError: if ripgrep is missing, the query/folder are invalid, or
            ripgrep exits with a genuine error.
    """
    if not options.query.strip():
        raise RipgrepError("Enter a search term first.")

    folder = Path(options.folder)
    if not options.folder or not folder.is_dir():
        raise RipgrepError("Selected folder does not exist.")

    if not ripgrep_available():
        raise RipgrepError("ripgrep is not installed or not found in PATH.")

    command = build_command(options)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:  # pragma: no cover - defensive
        raise RipgrepError(f"Failed to run ripgrep: {exc}") from exc

    if completed.returncode > _RG_NO_MATCH:
        message = completed.stderr.strip() or "ripgrep exited with an error."
        raise RipgrepError(message)

    results = parse_rg_output(completed.stdout)
    return results, completed.stderr.strip()
