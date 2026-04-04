import re
from textwrap import dedent as d

import pytest


@pytest.mark.parametrize("onlyopt", (None, "name", "email"))
def test_read_authors_from_pyproject(chdir, tmp_path, run_line, onlyopt):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "8.0.7"
            authors = [
              { name = "Foo", email = "foo@example.org" },
            ]
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    cmd = "mddj read authors"
    expect_out = "Foo <foo@example.org>"
    if onlyopt:
        cmd = f"{cmd} --only {onlyopt}"
        if onlyopt == "name":
            expect_out = "Foo"
        else:
            expect_out = "foo@example.org"

    expect_out = "^" + re.escape(expect_out) + "$"

    with chdir(tmp_path):
        run_line(cmd, search_stdout=expect_out)


@pytest.mark.parametrize("onlyopt", (None, "name", "email"))
def test_read_authors_from_build(chdir, tmp_path, run_line, onlyopt):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    cmd = "mddj read authors"
    if onlyopt:
        cmd = f"{cmd} --only {onlyopt}"

    # test that the expected outputs appear separately in the "both" case (any order)
    # because setuptools can't know to combine `author` and `author_email` (and
    # therefore will write them out separately)
    if onlyopt == "name":
        expect_out = ["^Foo$"]
    elif onlyopt == "email":
        expect_out = [r"^foo@example\.org$"]
    else:
        expect_out = ["^Foo$", r"^<foo@example\.org>$"]

    with chdir(tmp_path):
        run_line(cmd, search_stdout=expect_out)
