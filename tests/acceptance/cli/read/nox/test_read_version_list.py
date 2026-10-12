import pathlib
from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import LineRunner
from tests.types import ChdirType

nox = pytest.importorskip("nox")


def test_read_version_list_simple(
    chdir: ChdirType, tmp_path: pathlib.Path, run_line: LineRunner
) -> None:
    noxfile = tmp_path / "noxfile.py"

    noxfile.write_text(
        d("""\
            import nox

            @nox.session(python=("3.10", "3.11"))
            def test(session):
                pass
            """),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read nox list-versions")

    assert result.stdout == "3.10\n3.11\n"


def test_read_version_list_from_subdirectory(
    chdir: ChdirType, tmp_path: pathlib.Path, run_line: LineRunner
) -> None:
    noxfile = tmp_path / "noxfile.py"

    noxfile.write_text(
        d("""\
            import nox

            @nox.session(python=("3.8", "3.10", "3.11"))
            def test(session):
                pass
            """),
        encoding="utf-8",
    )

    subdir = tmp_path / "otherdir"
    subdir.mkdir()

    with chdir(subdir):
        result = run_line("mddj read nox list-versions")

    assert result.stdout == "3.8\n3.10\n3.11\n"


def test_read_version_list_no_listed_versions(
    chdir: ChdirType, tmp_path: pathlib.Path, run_line: LineRunner
) -> None:
    noxfile = tmp_path / "noxfile.py"

    noxfile.write_text(
        d("""\
            import nox

            @nox.session
            def test(session):
                pass
            """),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read nox list-versions")

    assert result.stdout == ""
    assert "Warning: no python versions detected from noxfile." in result.stderr


def test_read_version_list_empty_file_failure(
    chdir: ChdirType, tmp_path: pathlib.Path, run_line: LineRunner
) -> None:
    noxfile = tmp_path / "noxfile.py"

    noxfile.write_text(
        d("""\
            # zilch!
            """),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read nox list-versions", assert_exit_code=1)

    assert result.stdout == ""
    assert "NoxReaderError: nox listing failed" in result.stderr
