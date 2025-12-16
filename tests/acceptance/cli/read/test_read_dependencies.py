from textwrap import dedent as d


def test_read_dependencies_pyproject_toml(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"
            authors = [
              { name = "Foo", email = "foo@example.org" },
            ]
            dependencies = ["foo", "bar<2"]
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read dependencies")
        assert result.stdout == "foo\nbar<2\n"


def test_read_dependencies_from_setupcfg(chdir, tmp_path, run_line, capfd):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org

            [options]
            install_requires =
                foo
                bar<2
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read dependencies")
        assert result.stdout == "foo\nbar<2\n"
    captured = capfd.readouterr()
    assert captured.out == ""
