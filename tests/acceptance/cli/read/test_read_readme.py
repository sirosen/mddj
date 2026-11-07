import re
import tomllib
import typing as t
from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


def _read_toml_literal(data: str) -> t.Any:
    return tomllib.loads(f"data = {data}")["data"]


@pytest.mark.parametrize("content", (True, False))
@pytest.mark.parametrize(
    "value_literal",
    (
        '"README.md"',
        '{file = "README.md"}',
        '{file = "README.md", content-type = "text/markdown"}',
        '{file = "README.md", content-type = "text/markdown", charset = "UTF-8"}',
        '{text = "foopkg is way cool"}',
    ),
)
def test_read_readme(cli_env: CliEnv, content: bool, value_literal: str) -> None:
    cli_env.pyproject.write_text(
        d(f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            readme = {value_literal}
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()
    (cli_env.dir / "README.md").write_text(
        "fookpkg is very cool",
        encoding="utf-8",
    )

    toml_value = _read_toml_literal(value_literal)
    if content:
        match toml_value:
            case {"text": text}:
                expect_result = text
            case _:
                expect_result = r"^fookpkg is very cool$"
    else:
        match toml_value:
            case str() as stringval:
                expect_result = stringval
            case {"file": filename, "content-type": content_type}:
                expect_result = re.escape(d(f"""\
                    content-type: {content_type}
                    file:         {filename}
                    """))
            case {"file": filename, "content-type": content_type, "charset": charset}:
                expect_result = re.escape(d(f"""\
                    charset:      {charset}
                    content-type: {content_type}
                    file:         {filename}
                    """))
            case {"file": filename}:
                expect_result = re.escape(d(f"""\
                    file: {filename}
                    """))
            case {"text": text}:
                expect_result = re.escape(d(f"""\
                    text:

                    {text}
                    """))
            case _ as unreachable:
                raise NotImplementedError(unreachable)

    with cli_env.chdir():
        cmd = ["mddj", "read", "readme"]
        if content:
            cmd.append("--content")

        cli_env.run_line(cmd, search_stdout=expect_result)


@pytest.mark.parametrize("content", (True, False))
def test_read_readme_file_from_setupcfg(cli_env: CliEnv, content: bool) -> None:
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0
            long_description = file: README.md
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()
    (cli_env.dir / "README.md").write_text(
        "fookpkg is very cool",
        encoding="utf-8",
    )

    with cli_env.chdir():
        cmd = ["mddj", "read", "readme"]
        if content:
            cmd.append("--content")

        expect_result = r"^fookpkg is very cool$" if content else re.escape(d("""\
                content-type: text/x-rst
                text:

                fookpkg is very cool
                """))
        cli_env.run_line(cmd, search_stdout=expect_result)


@pytest.mark.parametrize("content", (True, False))
def test_read_short_readme_from_setupcfg(cli_env: CliEnv, content: bool) -> None:
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0
            long_description = a very good description
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        cmd = ["mddj", "read", "readme"]
        if content:
            cmd.append("--content")

        expect_result = r"^a very good description$" if content else re.escape(d("""\
                content-type: text/x-rst
                text:

                a very good description
                """))
        cli_env.run_line(cmd, search_stdout=expect_result)
