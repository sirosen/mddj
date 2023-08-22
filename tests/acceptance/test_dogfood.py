"""
self-tests of mddj
"""

import os
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent


@pytest.fixture(autouse=True)
def _in_repo_root():
    old_cwd = os.getcwd()
    os.chdir(REPO_ROOT)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def test_requires_python(run_line):
    run_line("mddj read requires-python", search_stdout=r"^>=3\.8$")
