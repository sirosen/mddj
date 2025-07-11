import pytest


def test_read_python_requires(tmpdir, run_line, capfd):
    setupcfg = tmpdir.join("setup.cfg")

    setupcfg.write(
        """\
[metadata]
name = foopkg
version = 1.0.0

author = Foo
author_email = foo@example.org

[options]
python_requires = >=3.10
"""
    )
    tmpdir.join("setup.py").write("from setuptools import setup; setup()\n")
    tmpdir.join("foopkg.py").write("")

    with tmpdir.as_cwd():
        result = run_line("mddj read requires-python", search_stdout=r"^>=3\.10$")
        assert len(result.stdout.splitlines()) == 1
    captured = capfd.readouterr()
    assert captured.out == ""


def test_read_python_requires_with_full_build_output_shows_all_data(
    tmpdir, run_line, capfd
):
    setupcfg = tmpdir.join("setup.cfg")

    setupcfg.write(
        """\
[metadata]
name = foopkg
version = 1.0.0

author = Foo
author_email = foo@example.org

[options]
python_requires = >=3.10
"""
    )
    tmpdir.join("setup.py").write("from setuptools import setup; setup()\n")
    tmpdir.join("foopkg.py").write("")

    with tmpdir.as_cwd():
        result = run_line(
            "mddj read requires-python",
            search_stdout=r"^>=3\.10$",
            env={"MDDJ_CAPTURE_BUILD_OUTPUT": "false"},
        )
        assert len(result.stdout.splitlines()) == 1

    captured = capfd.readouterr()
    assert len(captured.out.splitlines()) > 1
    assert "running dist_info" in captured.out


def test_read_version_from_build(tmpdir, run_line):
    setupcfg = tmpdir.join("setup.cfg")

    setupcfg.write(
        """\
[metadata]
name = foopkg
version = 1.0.0

author = Foo
author_email = foo@example.org
"""
    )
    tmpdir.join("setup.py").write("from setuptools import setup; setup()\n")
    tmpdir.join("foopkg.py").write("")

    with tmpdir.as_cwd():
        run_line("mddj read version", search_stdout=r"^1\.0\.0$")


@pytest.mark.parametrize("quote_char", ("", '"', "'"))
def test_update_version_assignment(tmpdir, run_line, quote_char):
    setupcfg = tmpdir.join("setup.cfg")
    pyproject = tmpdir.join("pyproject.toml")
    pyproject.write(
        """\
[tool.mddj]
write_version = "assign:setup.cfg:version"
"""
    )

    setupcfg.write(
        f"""\
[metadata]
name = foopkg
version = {quote_char}1.0.0{quote_char}
author = Foo
author_email = foo@example.org
"""
    )

    with tmpdir.as_cwd():
        run_line("mddj write version 1.0.1")

    assert setupcfg.read() == (
        f"""\
[metadata]
name = foopkg
version = {quote_char}1.0.1{quote_char}
author = Foo
author_email = foo@example.org
"""
    )
