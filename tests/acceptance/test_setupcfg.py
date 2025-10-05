import contextlib
from textwrap import dedent as d

import pytest


def test_read_python_requires(tmp_path, run_line, capfd):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org

            [options]
            python_requires = >=3.10
            """
        )
    )
    (tmp_path / "setup.py").write_text("from setuptools import setup; setup()\n")
    (tmp_path / "foopkg.py").touch()

    with contextlib.chdir(tmp_path):
        result = run_line("mddj read requires-python", search_stdout=r"^>=3\.10$")
        assert len(result.stdout.splitlines()) == 1
    captured = capfd.readouterr()
    assert captured.out == ""


def test_read_python_requires_with_full_build_output_shows_all_data(
    tmp_path, run_line, capfd
):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org

            [options]
            python_requires = >=3.10
            """
        )
    )
    (tmp_path / "setup.py").write_text("from setuptools import setup; setup()\n")
    (tmp_path / "foopkg.py").touch()

    with contextlib.chdir(tmp_path):
        result = run_line(
            "mddj read requires-python",
            search_stdout=r"^>=3\.10$",
            env={"MDDJ_CAPTURE_BUILD_OUTPUT": "false"},
        )
        assert len(result.stdout.splitlines()) == 1

    captured = capfd.readouterr()
    assert len(captured.out.splitlines()) > 1
    assert "running dist_info" in captured.out


def test_read_version_from_build(tmp_path, run_line):
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
        )
    )
    (tmp_path / "setup.py").write_text("from setuptools import setup; setup()\n")
    (tmp_path / "foopkg.py").touch()

    with contextlib.chdir(tmp_path):
        run_line("mddj read version", search_stdout=r"^1\.0\.0$")


@pytest.mark.parametrize("quote_char", ("", '"', "'"))
def test_update_version_assignment(tmp_path, run_line, quote_char):
    setupcfg = tmp_path / "setup.cfg"
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        d(
            """\
            [tool.mddj]
            write_version = "assign:setup.cfg:version"
            """
        )
    )

    setupcfg.write_text(
        d(
            f"""\
            [metadata]
            name = foopkg
            version = {quote_char}1.0.0{quote_char}
            author = Foo
            author_email = foo@example.org
            """
        )
    )

    with contextlib.chdir(tmp_path):
        run_line("mddj write version 1.0.1")

    assert setupcfg.read_text() == d(
        f"""\
        [metadata]
        name = foopkg
        version = {quote_char}1.0.1{quote_char}
        author = Foo
        author_email = foo@example.org
        """
    )
