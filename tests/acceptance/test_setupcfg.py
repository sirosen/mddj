import pytest


def test_read_python_requires(tmpdir, run_line):
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
        run_line("mddj read requires-python", search_stdout=r"^>=3\.10$")


@pytest.mark.parametrize("quote_char", ("", '"', "'"))
def test_update_version_assignment(tmpdir, run_line, quote_char):
    setupcfg = tmpdir.join("setup.cfg")
    pyproject = tmpdir.join("pyproject.toml")
    pyproject.write(
        """\
[tool.mddj]
version_path = "setup.cfg"
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
