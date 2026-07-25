from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


@pytest.mark.parametrize("quote_char", ('"', "'"))
def test_update_version_in_pyproject_toml(cli_env: CliEnv, quote_char: str) -> None:
    cli_env.pyproject.write_text(
        d(f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = {quote_char}1.0.0{quote_char}
            authors = [
              {{ name = "Foo", email = "foo@example.org" }},
            ]
            """),
        encoding="utf-8",
    )

    with cli_env.chdir():
        cli_env.run_line("mddj write version 2.3.1")

    assert cli_env.pyproject.read_text() == d(f"""\
        [build-system]
        requires = ["setuptools"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "foopkg"
        version = {quote_char}2.3.1{quote_char}
        authors = [
          {{ name = "Foo", email = "foo@example.org" }},
        ]
        """)


@pytest.mark.parametrize("quote_char", ("", '"', "'"))
def test_update_version_in_setup_cfg(cli_env: CliEnv, quote_char: str) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [tool.mddj]
            write_version = "assign:setup.cfg:version"
            """),
        encoding="utf-8",
    )

    cli_env.setupcfg.write_text(
        d(f"""\
            [metadata]
            name = foopkg
            version = {quote_char}1.0.0{quote_char}
            author = Foo
            author_email = foo@example.org
            """),
        encoding="utf-8",
    )

    with cli_env.chdir():
        cli_env.run_line("mddj write version 1.0.1")

    assert cli_env.setupcfg.read_text() == d(f"""\
        [metadata]
        name = foopkg
        version = {quote_char}1.0.1{quote_char}
        author = Foo
        author_email = foo@example.org
        """)
