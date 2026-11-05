from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


@pytest.mark.parametrize("quote_char", ('"', "'"))
def test_update_requires_python(cli_env: CliEnv, quote_char: str) -> None:
    cli_env.pyproject.write_text(
        d(f"""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            requires-python = {quote_char}>= 3.9{quote_char}
            """),
        encoding="utf-8",
    )

    with cli_env.chdir():
        cli_env.run_line("mddj write requires-python 3.12")

    assert cli_env.pyproject.read_text() == d(f"""\
        [build-system]
        requires = ["setuptools"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "foopkg"
        version = "1.0.0"
        requires-python = {quote_char}>=3.12{quote_char}
        """)


def test_update_requires_python_verbatim(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            requires-python = ">= 3.9"
            """),
        encoding="utf-8",
    )

    with cli_env.chdir():
        cli_env.run_line("mddj write requires-python --verbatim '>=3.12, !=3.12.0'")

    assert cli_env.pyproject.read_text() == d("""\
        [build-system]
        requires = ["setuptools"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "foopkg"
        version = "1.0.0"
        requires-python = ">=3.12, !=3.12.0"
        """)


def test_update_requires_python_rejects_non_version_inputs_by_default(
    cli_env: CliEnv,
) -> None:
    cli_env.pyproject.write_text(
        d("""\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            requires-python = ">= 3.9"
            """),
        encoding="utf-8",
    )

    with cli_env.chdir():
        result = cli_env.run_line(
            "mddj write requires-python '>=3.12, !=3.12.0'", assert_exit_code=1
        )

    assert result.stdout.startswith(
        "requires-python lower bounds must be Python 3.x version numbers"
    )
