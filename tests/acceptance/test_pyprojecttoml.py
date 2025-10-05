import contextlib
import re
from textwrap import dedent as d

import pytest


def test_read_python_requires(tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            authors = [
              { name = "Foo", email = "foo@example.org" },
            ]
            requires-python = ">=3.11"
            """
        )
    )
    (tmp_path / "foopkg.py").touch()

    with contextlib.chdir(tmp_path):
        run_line("mddj read requires-python", search_stdout=r"^>=3\.11$")


@pytest.mark.parametrize("quote_char", ('"', "'"))
def test_update_version_assignment(tmp_path, run_line, quote_char):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = {quote_char}1.0.0{quote_char}
            authors = [
              {{ name = "Foo", email = "foo@example.org" }},
            ]
            """
        )
    )

    with contextlib.chdir(tmp_path):
        run_line("mddj write version 2.3.1")

    assert pyproject.read_text() == d(
        f"""\
        [build-system]
        requires = ["setuptools"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "foopkg"
        version = {quote_char}2.3.1{quote_char}
        authors = [
          {{ name = "Foo", email = "foo@example.org" }},
        ]
        """
    )


def test_read_version_from_pyproject(tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "8.0.7"
            authors = [
              { name = "Foo", email = "foo@example.org" },
            ]
            """
        )
    )
    (tmp_path / "foopkg.py").write_text("")

    with contextlib.chdir(tmp_path):
        run_line("mddj read version", search_stdout=r"^8\.0\.7$")


@pytest.mark.parametrize(
    ("version", "attr", "result"),
    (
        ("9.7.5", "major", "9"),
        ("9.7.5", "minor", "7"),
        ("9.7.5", "micro", "5"),
        ("9.7.5a3", "pre", "a3"),
        ("9.7.5b3", "pre", "b3"),
        ("9.7.5rc3", "pre", "rc3"),
        ("9.7.5post1", "post", "1"),
        ("9.7.5.post1", "post", "1"),
        ("9.7.5rc1", "release", "9.7.5"),
    ),
)
def test_read_version_attribute_from_pyproject(
    tmp_path, run_line, version, attr, result
):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "{version}"
            authors = [
              {{ name = "Foo", email = "foo@example.org" }},
            ]
            """
        )
    )
    (tmp_path / "foopkg.py").write_text("")

    with contextlib.chdir(tmp_path):
        run_line(
            f"mddj read version --attr {attr}",
            search_stdout="^" + re.escape(result) + "$",
        )


@pytest.mark.parametrize(
    ("version", "attr", "message"),
    (
        pytest.param("9.7.5", "pre", "'9.7.5' is not a prerelease", id="pre"),
        pytest.param("2.0-dev1", "post", "'2.0-dev1' is not a post-release", id="post"),
    ),
)
def test_read_version_attribute_from_pyproject_fails_due_to_type(
    tmp_path, run_line, version, attr, message
):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "{version}"
            authors = [
              {{ name = "Foo", email = "foo@example.org" }},
            ]
            """
        )
    )
    (tmp_path / "foopkg.py").write_text("")

    with contextlib.chdir(tmp_path):
        run_line(
            f"mddj read version --attr {attr}",
            search_stderr="^" + re.escape(message) + "$",
            assert_exit_code=1,
        )
