from textwrap import dedent as d

import pytest


@pytest.mark.parametrize("lower_bound", (True, False))
def test_read_python_requires(chdir, tmp_path, run_line, lower_bound):
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
            requires-python = ">=3.11"
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        cmd = ["mddj", "read", "requires-python"]
        if lower_bound:
            cmd.append("--lower-bound")

        expect_result = r"^3\.11$" if lower_bound else r"^>=3\.11$"
        run_line(cmd, search_stdout=expect_result)


def test_read_python_requires_from_setupcfg(chdir, tmp_path, run_line, capfd):
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
            python_requires = >=3.10
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read requires-python", search_stdout=r"^>=3\.10$")
        assert len(result.stdout.splitlines()) == 1
    captured = capfd.readouterr()
    assert captured.out == ""
