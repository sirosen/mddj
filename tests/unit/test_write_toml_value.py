from textwrap import dedent as d

import pytest

from mddj.writers import write_toml_value


def test_write_table_key(tmp_path):
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

    write_result = write_toml_value(pyproject, "project.version", "1.1.0")
    assert write_result == "1.0.0"
    assert pyproject.read_text() == d(
        """\
        [project]
        version = "1.1.0"
        """
    )


def test_write_inline_table_key(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            project = {version = "1.0.0"}
            """
        ),
        encoding="utf-8",
    )

    write_result = write_toml_value(pyproject, "project.version", "1.1.0")
    assert write_result == "1.0.0"
    assert pyproject.read_text() == d(
        """\
        project = {version = "1.1.0"}
        """
    )


def test_write_at_top_level(tmp_path):
    config = tmp_path / "config.toml"

    config.write_text(
        d(
            """\
            version = "1.0.0"
            """
        ),
        encoding="utf-8",
    )

    write_result = write_toml_value(config, "version", "1.1.0")
    assert write_result == "1.0.0"
    assert config.read_text() == d(
        """\
        version = "1.1.0"
        """
    )


def test_write_array_element(tmp_path):
    config = tmp_path / "config.toml"

    config.write_text(
        d(
            """\
            flags = [
                "--verbose",
                "--okay",
            ]
            """
        ),
        encoding="utf-8",
    )

    write_result = write_toml_value(config, "flags.0", "--quiet")
    assert write_result == "--verbose"
    assert config.read_text() == d(
        """\
        flags = [
            "--quiet",
            "--okay",
        ]
        """
    )


def test_write_aot_table(tmp_path):
    config = tmp_path / "config.toml"

    config.write_text(
        d(
            """\
            [[projects]]
            version = "1.0.0"
            """
        ),
        encoding="utf-8",
    )

    write_result = write_toml_value(config, "projects.0.version", "1.1.0")
    assert write_result == "1.0.0"
    assert config.read_text() == d(
        """\
        [[projects]]
        version = "1.1.0"
        """
    )


def test_error_on_empty_path():
    with pytest.raises(ValueError, match="Cannot traverse an empty TOML path"):
        write_toml_value("foo.toml", "", "bar")


def test_top_level_key_must_be_str(tmp_path):
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

    with pytest.raises(
        ValueError, match="The first key of a TOML path must be a string"
    ):
        write_toml_value(pyproject, "1.bar", "baz")


def test_terminal_non_string_value_error(tmp_path):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [project]
            version = ["1.0.0"]
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="TOML path terminated in a non-string value"):
        write_toml_value(pyproject, "project.version", "2.0")


def test_scalar_value_at_destination(tmp_path):
    config = tmp_path / "config.toml"

    config.write_text(
        d(
            """\
            [foo]
            bar = "1.0.0"
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Nontrivial TOML write path must terminate in a table or array",
    ):
        write_toml_value(config, "foo.bar.baz", "2.0")


def test_traversal_crosses_scalar_value(tmp_path):
    config = tmp_path / "config.toml"

    config.write_text(
        d(
            """\
            [foo]
            bar = "1.0.0"
            """
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError, match=r"TOML path attempted to traverse scalar at \['foo', 'bar'\]"
    ):
        write_toml_value(config, "foo.bar.baz.quux", "2.0")
