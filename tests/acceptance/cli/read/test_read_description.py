from textwrap import dedent as d


def test_read_simple_project_attrs(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"
    toml_text = d(
        """\
        [project]
        name = "mypkg"
        version = "1.2.4"
        description = "A very cool package"
        """
    )
    pyproject.write_text(toml_text, encoding="utf-8")

    with chdir(tmp_path):
        cmd = ["mddj", "read", "description"]

        run_line(cmd, search_stdout=r"^A very cool package$")
