import pathlib
import sys

import pytest

from mddj._internal import _discovery
from mddj.api.reader.nox import NoxReader, NoxReaderError, _NoxReaderImplementation

try:
    import nox  # noqa: F401

    has_nox = True
except ImportError:
    has_nox = False


@pytest.fixture
def noxreader(tmp_path: pathlib.Path) -> NoxReader:
    dir_explorer = _discovery.DirExplorer(tmp_path)
    return _NoxReaderImplementation(dir_explorer)


@pytest.mark.skipif(not has_nox, reason="Test requires nox import")
def test_nox_command_discovery_when_importable(noxreader: NoxReader) -> None:
    cmd = noxreader._nox_cmd
    assert cmd == (sys.executable, "-m", "nox")


@pytest.mark.skipif(has_nox, reason="Test requires that nox import fails")
def test_nox_command_discovery_when_not_importable(
    noxreader: NoxReader, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("shutil.which", lambda *args: "/usr/bin/nox")
    cmd = noxreader._nox_cmd
    assert cmd == ("/usr/bin/nox",)


@pytest.mark.skipif(has_nox, reason="Test requires that nox import fails")
def test_nox_command_discovery_failure(
    noxreader: NoxReader, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("shutil.which", lambda *args: None)
    with pytest.raises(
        NoxReaderError, match="Cannot fetch nox data. A 'nox' command was not found."
    ):
        noxreader._nox_cmd
