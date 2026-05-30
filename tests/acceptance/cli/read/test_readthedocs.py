from textwrap import dedent as d

import pytest


@pytest.mark.parametrize("extension", ("yaml", "yml"))
def test_read_python_version_default(chdir, tmp_path, run_line, extension):
    (tmp_path / "pyproject.toml").touch()

    rtd_yaml = tmp_path / f".readthedocs.{extension}"

    rtd_yaml.write_text(d("""\
            version: 2
            build:
              os: ubuntu-24.04
              tools:
                python: "3.13"
            """))

    with chdir(tmp_path):
        run_line("mddj read readthedocs python-version", search_stdout=r"^3\.13$")


def test_read_python_version_from_uv_tool_install(chdir, tmp_path, run_line):
    (tmp_path / "pyproject.toml").write_text(d("""\
            [tool.mddj.readthedocs]
            python_version_path = "build.commands"
            python_version_extraction = "parse_uv_tool_install"
            """))

    rtd_yaml = tmp_path / ".readthedocs.yaml"

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

    with chdir(tmp_path):
        run_line("mddj read readthedocs python-version", search_stdout=r"^3\.14$")
