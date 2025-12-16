from textwrap import dedent as d

import pytest


@pytest.mark.parametrize("quote_char", ('"', "'"))
def test_update_version_in_pyproject_toml(chdir, tmp_path, run_line, quote_char):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
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
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        run_line("mddj write version 2.3.1")

    assert pyproject.read_text() == d(
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


@pytest.mark.parametrize("quote_char", ("", '"', "'"))
def test_update_version_in_setup_cfg(chdir, tmp_path, run_line, quote_char):
    setupcfg = tmp_path / "setup.cfg"
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        d(
            """\
            [tool.mddj]
            write_version = "assign:setup.cfg:version"
            """
        ),
        encoding="utf-8",
    )

    setupcfg.write_text(
        d(
            f"""\
            [metadata]
            name = foopkg
            version = {quote_char}1.0.0{quote_char}
            author = Foo
            author_email = foo@example.org
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        run_line("mddj write version 1.0.1")

    assert setupcfg.read_text() == d(
        f"""\
        [metadata]
        name = foopkg
        version = {quote_char}1.0.1{quote_char}
        author = Foo
        author_email = foo@example.org
        """
    )
