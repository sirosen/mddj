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
    run_line("mddj read requires-python", search_stdout=r"^>=3\.10$")


def test_say_my_name(run_line):
    run_line("mddj read name", search_stdout=r"^mddj$")


def test_my_import_names_are_stated(run_line):
    run_line("mddj read import-names", search_stdout=r"^mddj$")


def test_i_have_no_namespaces(run_line):
    result = run_line("mddj read import-namespaces")
    assert result.stdout == ""
