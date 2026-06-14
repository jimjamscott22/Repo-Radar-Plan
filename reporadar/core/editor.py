"""Open search results in the user's preferred editor."""

from __future__ import annotations

import shutil
import subprocess


class EditorError(Exception):
    """Raised when a result cannot be opened in an editor."""


# Maps a settings key to the command template for opening a file at a line.
# ``{file}`` and ``{line}`` are substituted before execution.
EDITOR_COMMANDS: dict[str, list[str]] = {
    "code": ["code", "-g", "{file}:{line}"],
    "cursor": ["cursor", "-g", "{file}:{line}"],
    "default": ["xdg-open", "{file}"],
}


def _binary_name(template: list[str]) -> str:
    return template[0]


def open_result(
    file_path: str,
    line_number: int,
    editor: str = "cursor",
    custom_command: str | None = None,
) -> None:
    """Open ``file_path`` at ``line_number`` in the configured editor.

    ``editor`` is one of ``code``, ``cursor``, ``default`` or ``custom``. When
    ``custom``, ``custom_command`` is a template string that may contain
    ``{file}`` and ``{line}`` placeholders.

    Raises:
        EditorError: if the editor command is missing or fails to launch.
    """
    if editor == "custom":
        if not custom_command:
            raise EditorError("No custom editor command configured.")
        template = custom_command.split()
    else:
        template = EDITOR_COMMANDS.get(editor)
        if template is None:
            raise EditorError(f"Unknown editor: {editor!r}")

    command = [
        part.replace("{file}", file_path).replace("{line}", str(line_number))
        for part in template
    ]

    if shutil.which(_binary_name(command)) is None:
        raise EditorError(
            f"Could not open editor. '{_binary_name(command)}' was not found in PATH."
        )

    try:
        subprocess.Popen(command)  # noqa: S603 - args are a list, not a shell string
    except OSError as exc:
        raise EditorError(f"Could not open editor: {exc}") from exc
