"""Tests for the ripgrep output parser."""

from __future__ import annotations

from reporadar.core.result_parser import parse_line, parse_rg_output


def test_parse_normal_line():
    result = parse_line("src/app.py:42:13:# TODO: clean this up later")
    assert result is not None
    assert result.file_path == "src/app.py"
    assert result.line_number == 42
    assert result.column_number == 13
    assert result.line_text == "# TODO: clean this up later"


def test_parse_line_with_colons_in_match():
    result = parse_line("a.py:1:1:url = http://example.com:8080")
    assert result is not None
    assert result.line_text == "url = http://example.com:8080"


def test_parse_empty_output():
    assert parse_rg_output("") == []


def test_parse_multiple_results():
    output = "a.py:1:1:foo\nb.py:2:3:bar\n"
    results = parse_rg_output(output)
    assert len(results) == 2
    assert results[1].file_path == "b.py"


def test_parse_invalid_line_returns_none():
    assert parse_line("not a valid line") is None
    assert parse_line("file.py:notanumber:1:text") is None
    assert parse_line("") is None


def test_parse_output_skips_blank_lines():
    output = "a.py:1:1:foo\n\nb.py:2:2:bar\n"
    assert len(parse_rg_output(output)) == 2
