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
