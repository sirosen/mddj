from textwrap import dedent as d

from tests.acceptance.conftest import CliEnv


def test_read_name_from_pyproject_toml(cli_env: CliEnv) -> None:
    toml_text = d("""\
        [project]
        name = "mypkg"
        version = "1.2.4"
        """)
    cli_env.pyproject.write_text(toml_text, encoding="utf-8")

    with cli_env.chdir():
        cmd = ["mddj", "read", "name"]

        cli_env.run_line(cmd, search_stdout=r"^mypkg$")


def test_read_name_from_full_build(cli_env: CliEnv) -> None:
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read name", search_stdout=r"^foopkg$")
        assert len(result.stdout.splitlines()) == 1
