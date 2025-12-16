from textwrap import dedent as d

import pytest

pytest.importorskip("tox")


def test_read_version_list_simple(chdir, tmp_path, run_line):
    toxini = tmp_path / "tox.ini"

    toxini.write_text(
        d(
            """\
            [tox]
            envlist = py{36,37,38,35,39,310}

            [testenv]
            commands = python -m pytest
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read tox list-versions")

    assert result.stdout == "3.5\n3.6\n3.7\n3.8\n3.9\n3.10\n"


def test_read_version_list_with_repeats_and_factors(chdir, tmp_path, run_line):
    toxini = tmp_path / "tox.ini"

    toxini.write_text(
        d(
            """\
            [tox]
            envlist =
                py{36,37,38,35,39,310}
                py{35,310}-toml

            [testenv]
            commands = python -m pytest
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read tox list-versions")

    assert result.stdout == "3.5\n3.6\n3.7\n3.8\n3.9\n3.10\n"
