import pytest


def test_read_python_requires(tmpdir, run_line):
    pyproject = tmpdir.join("pyproject.toml")

    pyproject.write(
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
    )
    tmpdir.join("foopkg.py").write("")

    with tmpdir.as_cwd():
        run_line("mddj read requires-python", search_stdout=r"^>=3\.11$")


@pytest.mark.parametrize("quote_char", ('"', "'"))
def test_update_version_assignment(tmpdir, run_line, quote_char):
    pyproject = tmpdir.join("pyproject.toml")

    pyproject.write(
        f"""\
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "foopkg"
version = {quote_char}1.0.0{quote_char}
authors = [
  {{ name = "Foo", email = "foo@example.org" }},
]
"""
    )

    with tmpdir.as_cwd():
        run_line("mddj write version 2.3.1")

    assert pyproject.read() == (
        f"""\
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "foopkg"
version = {quote_char}2.3.1{quote_char}
authors = [
  {{ name = "Foo", email = "foo@example.org" }},
]
"""
    )
