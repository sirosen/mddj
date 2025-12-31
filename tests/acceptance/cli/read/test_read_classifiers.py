from textwrap import dedent as d


def test_read_static_classifiers(chdir, tmp_path, run_line):
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
            classifiers = [
              "Development Status :: 5 - Production",
              "Programming Language :: Python",
            ]
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read classifiers")
        assert result.stdout == d(
            """\
            Development Status :: 5 - Production
            Programming Language :: Python
            """
        )
