from textwrap import dedent as d

import pytest

pytest.importorskip("tox")


def test_read_min_version_success(chdir, tmp_path, run_line):
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
        run_line("mddj read tox min-version", search_stdout="3.5")
