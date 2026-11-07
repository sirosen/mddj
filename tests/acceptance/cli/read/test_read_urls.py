from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


@pytest.mark.parametrize("normalize", (True, False))
def test_read_urls_pyproject_toml(cli_env: CliEnv, normalize: bool) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.urls]
            Source = 'https://example.com/repo'
            Contact-Us = 'https://example.com/contact'
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        cmd = ["mddj", "read", "urls"]
        expect_output = d("""\
            Source = https://example.com/repo
            Contact-Us = https://example.com/contact
            """)
        if normalize:
            cmd.append("--normalize")
            expect_output = d("""\
                source = https://example.com/repo
                contactus = https://example.com/contact
                """)
        result = cli_env.run_line(cmd)
        assert result.stdout == expect_output


def test_read_single_url(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.urls]
            Source = 'https://example.com/repo'
            Contact-Us = 'https://example.com/contact'
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        cmd = ["mddj", "read", "urls", "--normalize", "--name", "source"]
        expect_output = d("""\
            https://example.com/repo
            """)
        result = cli_env.run_line(cmd)
        assert result.stdout == expect_output


@pytest.mark.parametrize("normalize", (True, False))
def test_read_urls_from_setupcfg(cli_env: CliEnv, normalize: bool) -> None:
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0
            project-urls =
                Source = https://example.com/repo
                Contact-Us = https://example.com/contact

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
        cmd = ["mddj", "read", "urls"]
        expect_output = d("""\
            Source = https://example.com/repo
            Contact-Us = https://example.com/contact
            """)
        if normalize:
            cmd.append("--normalize")
            expect_output = d("""\
                source = https://example.com/repo
                contactus = https://example.com/contact
                """)
        result = cli_env.run_line(cmd)
        assert result.stdout == expect_output
