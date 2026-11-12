import re
import tomllib
import typing as t
from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


def _read_toml_literal(data: str) -> t.Any:
    return tomllib.loads(f"data = {data}")["data"]


@pytest.mark.parametrize(
    ("license_value_literal", "license_files_literal"),
    (
        ('"MIT"', None),
        ('{file = "LICENSE.txt"}', None),
        ('{text = "Do what you like"}', None),
        ('"MIT"', '["LICENSE.txt"]'),
        ('"MIT"', '["AUTHORS.txt", "LICENSE.txt"]'),
    ),
)
def test_read_license(
    cli_env: CliEnv, license_value_literal: str, license_files_literal: str | None
) -> None:
    cli_env.pyproject.write_text(
        d(f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            license = {license_value_literal}
            """)
        + (
            "" if license_files_literal is None else d(f"""\
            license-files = {license_files_literal}
            """)
        ),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()
    (cli_env.dir / "README.md").write_text(
        "fookpkg is very cool",
        encoding="utf-8",
    )

    license_toml_value = _read_toml_literal(license_value_literal)
    license_files_toml_value = (
        _read_toml_literal(license_files_literal) if license_files_literal else None
    )
    match (license_toml_value, license_files_toml_value):
        case (str() as stringval, None):
            expect_result = f"expression: {stringval}"
        case ({"file": filename}, None):
            expect_result = re.escape(d(f"""\
                files:
                  - {filename!r}
                """))
        case ({"text": content}, None):
            expect_result = re.escape(d(f"""\
                text:

                {content}
                """))
        case (str() as stringval, files):
            assert files is not None
            expect_result = re.escape(d(f"""\
                expression: {stringval}
                files:
                """) + "\n".join(f"  - {f!r}" for f in files) + "\n")
        case _ as unreachable:
            raise NotImplementedError(unreachable)

    with cli_env.chdir():
        cmd = ["mddj", "read", "license"]

        cli_env.run_line(cmd, search_stdout=expect_result)


def test_read_license_from_setupcfg(cli_env: CliEnv) -> None:
    # Unlike pyproject.toml data handling, the data from setup.cfg is routed somewhat
    # ambiguously into the `License` metadata field, even when it is "obviously" a
    # license expression, not the full license text.
    # There's no clear fix for this, since setuptools behavior is part of what motivated
    # PEP 639 to clarify the text/expression distinction.
    cli_env.setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0
            license = BSD-3-Clause
            """),
        encoding="utf-8",
    )
    cli_env.setuppy.write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        cmd = ["mddj", "read", "license"]

        expect_result = "^" + re.escape("text:\n\nBSD-3-Clause") + "$"
        cli_env.run_line(cmd, search_stdout=expect_result)
