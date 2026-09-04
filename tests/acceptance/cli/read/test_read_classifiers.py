from textwrap import dedent as d

from tests.acceptance.conftest import CliEnv


def test_read_static_classifiers(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(
        d("""\
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
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read classifiers")
        assert result.stdout == d("""\
            Development Status :: 5 - Production
            Programming Language :: Python
            """)


def test_read_python_versions_from_classifiers(cli_env: CliEnv) -> None:
    cli_env.pyproject.write_text(
        d("""\
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
              "Programming Language :: Python :: 3",
              "Programming Language :: Python :: 2",
              "Programming Language :: Python :: 2.7",
              "Programming Language :: Python :: 3.5",
            ]
            """),
        encoding="utf-8",
    )
    (cli_env.dir / "foopkg.py").touch()

    with cli_env.chdir():
        result = cli_env.run_line("mddj read classifiers --python-versions")
        assert result.stdout == d("""\
            2.7
            3.5
            """)
