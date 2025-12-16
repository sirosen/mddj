from textwrap import dedent as d


def test_read_name_from_pyproject_toml(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"
    toml_text = d(
        """\
        [project]
        name = "mypkg"
        version = "1.2.4"
        """
    )
    pyproject.write_text(toml_text, encoding="utf-8")

    with chdir(tmp_path):
        cmd = ["mddj", "read", "name"]

        run_line(cmd, search_stdout=r"^mypkg$")


def test_read_name_from_full_build(chdir, tmp_path, run_line):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read name", search_stdout=r"^foopkg$")
        assert len(result.stdout.splitlines()) == 1
