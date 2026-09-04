from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import CliEnv


@pytest.mark.parametrize("extension", ("yaml", "yml"))
def test_read_python_version_default(cli_env: CliEnv, extension: str) -> None:
    cli_env.pyproject.touch()

    rtd_yaml = cli_env.dir / f".readthedocs.{extension}"

    rtd_yaml.write_text(d("""\
            version: 2
            build:
              os: ubuntu-24.04
              tools:
                python: "3.13"
            """))

    with cli_env.chdir():
        cli_env.run_line(
            "mddj read readthedocs python-version", search_stdout=r"^3\.13$"
        )


def test_read_python_version_from_uv_tool_install(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(d("""\
            [tool.mddj.readthedocs]
            python_version_path = "build.commands"
            python_version_extraction = "parse_uv_tool_install"
            """))

    rtd_yaml = cli_env.dir / ".readthedocs.yaml"

    rtd_yaml.write_text(d("""\
            version: 2

            build:
              os: ubuntu-24.04

              commands:
                - asdf plugin add uv
                - asdf install uv latest
                - asdf global uv latest

                - uv tool install tox --with tox-uv --python "3.14" --managed-python
                - uv tool run tox run -e docs -- "${READTHEDOCS_OUTPUT}"/html
            """))

    with cli_env.chdir():
        cli_env.run_line(
            "mddj read readthedocs python-version", search_stdout=r"^3\.14$"
        )
