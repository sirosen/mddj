from textwrap import dedent as d

from tests.acceptance.conftest import CliEnv


def test_read_simple_project_attrs(cli_env: CliEnv) -> None:
    toml_text = d("""\
        [project]
        name = "mypkg"
        version = "1.2.4"
        description = "A very cool package"
        """)
    cli_env.pyproject.write_text(toml_text, encoding="utf-8")

    with cli_env.chdir():
        cmd = ["mddj", "read", "description"]
        cli_env.run_line(cmd, search_stdout=r"^A very cool package$")
