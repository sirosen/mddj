import contextlib
import os
import sys
import types

import pytest

from tests.types import ChdirType


# remove this fixture once Python 3.10 support is done
@pytest.fixture(scope="session")
def chdir() -> ChdirType:
    if sys.version_info >= (3, 11):
        return contextlib.chdir

    # based on the contents of contextlib for py3.11+
    class chdir:
        def __init__(self, path: str | os.PathLike[str]) -> None:
            self.path = path
            self._old_cwd: list[str] = []

        def __enter__(self) -> None:
            self._old_cwd.append(os.getcwd())
            os.chdir(self.path)

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
        ) -> None:
            os.chdir(self._old_cwd.pop())

    return chdir
