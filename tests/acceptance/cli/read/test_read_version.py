import re
from textwrap import dedent as d

import pytest


def test_read_version_from_pyproject(chdir, tmp_path, run_line):
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
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").write_text("", encoding="utf-8")

    with chdir(tmp_path):
        run_line("mddj read version", search_stdout=r"^8\.0\.7$")


def test_read_version_from_build(chdir, tmp_path, run_line):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        run_line("mddj read version", search_stdout=r"^1\.0\.0$")


def test_read_version_from_build_with_pyproject_present(chdir, tmp_path, run_line):
    setupcfg = tmp_path / "setup.cfg"
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        d(
            """\
            [project]
            name = "foopkg"
            dynamic = ["version"]
            """
        )
    )

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        run_line("mddj read version", search_stdout=r"^1\.0\.0$")


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
    chdir, tmp_path, run_line, version, attr, result
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
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").write_text("", encoding="utf-8")

    with chdir(tmp_path):
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
    chdir, tmp_path, run_line, version, attr, message
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
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").write_text("", encoding="utf-8")

    with chdir(tmp_path):
        run_line(
            f"mddj read version --attr {attr}",
            search_stderr="^" + re.escape(message) + "$",
            assert_exit_code=1,
        )


@pytest.mark.parametrize(
    "bad_toml",
    (
        pytest.param(
            """\
            tool = 1
            """,
            id="tool-not-a-table",
        ),
        pytest.param(
            """\
            tool.mddj = 1
            """,
            id="tool.mddj-not-a-table",
        ),
    ),
)
def test_read_version_from_pyproject_ignores_malformed_tool_config(
    tmpdir, run_line, bad_toml
):
    pyproject = tmpdir.join("pyproject.toml")

    pyproject.write(
        d(
            f"""\
            {bad_toml}

            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "8.0.7"
            authors = [
              {{ name = "Foo", email = "foo@example.org" }},
            ]
            """
        )
    )
    tmpdir.join("foopkg.py").write("")

    with tmpdir.as_cwd():
        run_line("mddj read version", search_stdout=r"^8\.0\.7$")
