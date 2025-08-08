import pytest

from mddj._toml_path import ParseError, parse_toml_path


@pytest.mark.parametrize(
    "path, expect_result",
    [
        ("foo", ["foo"]),
        ("foo.bar", ["foo", "bar"]),
        ("foo.0.bar", ["foo", 0, "bar"]),
        ("foo.'0'.bar", ["foo", "0", "bar"]),
        ("foo\\.bar", ["foo.bar"]),
        ("foo\\\\.bar", ["foo\\", "bar"]),
        ("", []),
        ("''", [""]),
    ],
)
def test_valid_parse(path, expect_result):
    assert parse_toml_path(path) == expect_result


@pytest.mark.parametrize(
    "path, expect_message",
    [
        ("foo\\", "Terminal escape\\."),
        ("abc.", "Terminal '\\.' separator\\."),
        ("x..y", "Double '\\.' separator\\."),
        (
            "xy.foo'bar'",
            (
                "Quote chars within keys must be escaped "
                "or the entire key must be quoted\\."
            ),
        ),
        ("foo.'bar", "Unclosed quoted string\\."),
        ('foo."bar', "Unclosed quoted string\\."),
        ('foo."bar', "Unclosed quoted string\\."),
        (".x", "Leading '\\.' separator\\."),
    ],
)
def test_parse_error(path, expect_message):
    with pytest.raises(ParseError, match=expect_message):
        parse_toml_path(path)
