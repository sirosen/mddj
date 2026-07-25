from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


@pytest.mark.parametrize("lower_bound", (True, False))
def test_read_python_requires(cli_env: CliEnv, lower_bound: bool) -> None:
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
            requires-python = ">=3.11"
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        cmd = ["mddj", "read", "requires-python"]
        if lower_bound:
            cmd.append("--lower-bound")

        expect_result = r"^3\.11$" if lower_bound else r"^>=3\.11$"
        cli_env.run_line(cmd, search_stdout=expect_result)


def test_read_python_requires_from_setupcfg(
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
            python_requires = >=3.10
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line(
            "mddj read requires-python", search_stdout=r"^>=3\.10$"
        )
        assert len(result.stdout.splitlines()) == 1
    captured = capfd.readouterr()
    assert captured.out == ""
