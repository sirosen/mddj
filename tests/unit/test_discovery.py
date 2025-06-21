import pytest

from mddj.discovery import discover_project_dir


@pytest.mark.parametrize(
    "indicator_file", ("pyproject.toml", "setup.cfg", "setup.py", "tox.ini")
)
def test_can_discover_unambiguous_project_dir(monkeypatch, tmpdir, indicator_file):
    tmpdir.join(indicator_file).write("")

    working_dir = tmpdir.join("subdir")
    working_dir.mkdir()
    monkeypatch.chdir(working_dir)

    assert str(discover_project_dir()) == str(tmpdir)


def test_discovery_skips_setup_py_dir_with_init_py(monkeypatch, tmpdir):
    tmpdir.join("pyproject.toml").write("")

    module_dir = tmpdir.join("subdir1")
    module_dir.mkdir()

    module_dir.join("setup.py").write("")
    module_dir.join("__init__.py").write("")

    monkeypatch.chdir(module_dir)

    assert str(discover_project_dir()) == str(tmpdir)

    # removing the __init__.py changes discovery
    module_dir.join("__init__.py").remove()
    assert str(discover_project_dir()) == str(module_dir)


def test_discovery_selects_setup_py_at_repo_root_as_final_guess(monkeypatch, tmpdir):
    # "repo root"
    tmpdir.join("setup.py").write("")
    tmpdir.join(".git").mkdir()
    # but it contains an '__init__.py', so normally it would not be considered
    tmpdir.join("__init__.py").write("")

    subdir = tmpdir.join("subdir1")
    subdir.mkdir()

    monkeypatch.chdir(subdir)

    assert str(discover_project_dir()) == str(tmpdir)
