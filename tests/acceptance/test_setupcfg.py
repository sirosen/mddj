import pathlib
from textwrap import dedent as d

import pytest

from tests.acceptance.conftest import LineRunner
from tests.types import ChdirType


def test_read_python_requires_with_full_build_output_shows_all_data(
    chdir: ChdirType,
    tmp_path: pathlib.Path,
    run_line: LineRunner,
    capfd: pytest.CaptureFixture[str],
) -> None:
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d("""\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org

            [options]
            python_requires = >=3.10
            """),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line(
            "mddj read requires-python",
            search_stdout=r"^>=3\.10$",
            env={"MDDJ_CAPTURE_BUILD_OUTPUT": "false"},
        )
        assert len(result.stdout.splitlines()) == 1

    captured = capfd.readouterr()
    assert len(captured.out.splitlines()) > 1
    assert "running dist_info" in captured.out
