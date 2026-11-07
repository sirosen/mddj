from textwrap import dedent as d

from tests.acceptance.conftest import CliEnv


def test_read_entry_points_pyproject_toml(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.entry-points.foo-plugins]
            foopkg = 'foopkg._plugin:plugin'
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read entry-points")
        assert result.stdout == d("""\
            [foo-plugins]
            foopkg = foopkg._plugin:plugin
            """)


def test_read_entry_points_from_setupcfg(cli_env: CliEnv) -> None:
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0

            [options.entry_points]
            foo-plugins =
                foopkg = foopkg._plugin:plugin
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read entry-points")
        assert result.stdout == d("""\
            [foo-plugins]
            foopkg = foopkg._plugin:plugin
            """)
