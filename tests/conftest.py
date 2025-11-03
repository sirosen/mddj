import contextlib
import os
import sys

import pytest


# remove this fixture once Python 3.10 support is done
@pytest.fixture(scope="session")
def chdir():
    if sys.version_info >= (3, 11):
        return contextlib.chdir

    # based on the contents of contextlib for py3.11+
    class chdir:
        def __init__(self, path) -> None:
            self.path = path
            self._old_cwd = []

        def __enter__(self):
            self._old_cwd.append(os.getcwd())
            os.chdir(self.path)

        def __exit__(self, *excinfo):
            os.chdir(self._old_cwd.pop())

    return chdir
