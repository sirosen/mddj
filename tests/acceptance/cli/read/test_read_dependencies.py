from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


def test_read_dependencies_pyproject_toml(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            authors = [
              { name = "Foo", email = "foo@example.org" },
            ]
            dependencies = ["foo", "bar<2"]
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read dependencies")
        assert result.stdout == "foo\nbar<2\n"


def test_read_dependencies_from_setupcfg(
    cli_env: CliEnv, capfd: pytest.CaptureFixture[str]
) -> None:
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org

            [options]
            install_requires =
                foo
                bar<2
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read dependencies")
        assert result.stdout == "foo\nbar<2\n"
    captured = capfd.readouterr()
    assert captured.out == ""
