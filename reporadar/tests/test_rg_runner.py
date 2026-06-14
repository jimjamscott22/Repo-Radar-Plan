"""Tests for ripgrep command construction and search behavior."""

from __future__ import annotations

import pytest

from reporadar.core.models import SearchOptions
from reporadar.core.rg_runner import RipgrepError, build_command, run_search


def _opts(**kwargs) -> SearchOptions:
    base = {"query": "TODO", "folder": "."}
    base.update(kwargs)
    return SearchOptions(**base)


def test_build_basic_command():
    cmd = build_command(_opts())
    assert cmd[0] == "rg"
    assert "--line-number" in cmd
    assert "--column" in cmd
    assert "--no-heading" in cmd
    # Query and folder come after the ``--`` separator.
    assert cmd[-2] == "TODO"
    assert cmd[-1] == "."


def test_case_insensitive_flag():
    assert "-i" in build_command(_opts(case_insensitive=True))
    assert "-i" not in build_command(_opts(case_insensitive=False))


def test_whole_word_flag():
    assert "-w" in build_command(_opts(whole_word=True))


def test_fixed_string_flag():
    assert "-F" in build_command(_opts(fixed_string=True))


def test_hidden_and_no_ignore_flags():
    cmd = build_command(_opts(include_hidden=True, no_ignore=True))
    assert "--hidden" in cmd
    assert "--no-ignore" in cmd


def test_glob_filter():
    cmd = build_command(_opts(file_glob="*.py"))
    assert "-g" in cmd
    assert "*.py" in cmd


def test_query_starting_with_dash_is_not_a_flag():
    cmd = build_command(_opts(query="-i"))
    # The double-dash separator must appear before the query.
    assert "--" in cmd
    assert cmd.index("--") < cmd.index("-i", cmd.index("--"))


def test_empty_query_raises():
    with pytest.raises(RipgrepError):
        run_search(_opts(query="   "))


def test_missing_folder_raises():
    with pytest.raises(RipgrepError):
        run_search(_opts(folder="/nonexistent/path/xyz123"))


def test_run_search_finds_matches(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("x = 1  # TODO: refactor\nprint('ok')\n")
    results, _warning = run_search(_opts(query="TODO", folder=str(tmp_path)))
    assert len(results) == 1
    assert results[0].line_number == 1


def test_run_search_no_matches_is_not_error(tmp_path):
    (tmp_path / "a.py").write_text("clean code\n")
    results, _warning = run_search(_opts(query="ZZZZNOPE", folder=str(tmp_path)))
    assert results == []
