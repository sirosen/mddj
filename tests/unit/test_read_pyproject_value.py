from textwrap import dedent as d

import pytest

from mddj.readers import read_pyproject_toml_value


def test_read_string_table_key(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [project]
            version = "1.0.0"
            """
        )
    )

    read_val = read_pyproject_toml_value(pyproject, "project", "version")
    assert read_val == "1.0.0"


def test_read_array_members(tmp_path):
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
        )
    )

    read_val = read_pyproject_toml_value(pyproject, "mytable", "items", 0)
    assert read_val == "foo"


def test_read_bad_lookup_noncontainer(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [mytable]
            foo = "bar"
            """
        )
    )

    with pytest.raises(LookupError, match="Terminated in a non-container type"):
        read_pyproject_toml_value(pyproject, "mytable", "foo", "bar")


def test_read_bad_lookup_wrong_index_type(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [mytable]
            foo = ["bar"]
            """
        )
    )

    with pytest.raises(LookupError, match="Incorrect index type"):
        read_pyproject_toml_value(pyproject, "mytable", "foo", "bar")
