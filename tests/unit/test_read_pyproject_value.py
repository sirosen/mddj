from textwrap import dedent as d

import pytest

from mddj._internal import _cached_toml, _readers


@pytest.fixture
def document_cache():
    return _cached_toml.TomlDocumentCache()


def test_read_string_table_key(tmp_path, document_cache):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [project]
            version = "1.0.0"
            """
        ),
        encoding="utf-8",
    )

    read_val = _readers.read_pyproject_toml_value(
        document_cache.load(pyproject), "project", "version"
    )
    assert read_val == "1.0.0"


def test_read_array_members(tmp_path, document_cache):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [mytable]
            items = [
                "foo",
                "bar",
            ]
            """
        ),
        encoding="utf-8",
    )

    read_val = _readers.read_pyproject_toml_value(
        document_cache.load(pyproject), "mytable", "items", 0
    )
    assert read_val == "foo"


def test_read_bad_lookup_noncontainer(tmp_path, document_cache):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [mytable]
            foo = "bar"
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(LookupError, match="Terminated in a non-container type"):
        _readers.read_pyproject_toml_value(
            document_cache.load(pyproject), "mytable", "foo", "bar"
        )


def test_read_bad_lookup_wrong_index_type(tmp_path, document_cache):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [mytable]
            foo = ["bar"]
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(LookupError, match="Incorrect index type"):
        _readers.read_pyproject_toml_value(
            document_cache.load(pyproject), "mytable", "foo", "bar"
        )
