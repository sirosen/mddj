def test_read_min_version(tmpdir, run_line):
    toxini = tmpdir.join("tox.ini")

    toxini.write(
        """\
[tox]
envlist = py{36,37,38,35,39,310}

[testenv]
commands = python -m pytest
"""
    )

    with tmpdir.as_cwd():
        run_line("mddj read tox min-version", search_stdout="3.5")


def test_read_version_list(tmpdir, run_line):
    toxini = tmpdir.join("tox.ini")

    toxini.write(
        """\
[tox]
envlist = py{36,37,38,35,39,310}

[testenv]
commands = python -m pytest
"""
    )

    with tmpdir.as_cwd():
        result = run_line("mddj read tox list-versions")

    assert result.stdout == "3.5\n3.6\n3.7\n3.8\n3.9\n3.10\n"


def test_read_version_list_with_repeats_and_factors(tmpdir, run_line):
    toxini = tmpdir.join("tox.ini")

    toxini.write(
        """\
[tox]
envlist =
    py{36,37,38,35,39,310}
    py{35,310}-toml

[testenv]
commands = python -m pytest
"""
    )

    with tmpdir.as_cwd():
        result = run_line("mddj read tox list-versions")

    assert result.stdout == "3.5\n3.6\n3.7\n3.8\n3.9\n3.10\n"
