import pytest

from mddj._internal._discovery import discover_project_dir


@pytest.mark.parametrize(
    "indicator_file", ("pyproject.toml", "setup.cfg", "setup.py", "tox.ini")
)
def test_can_discover_unambiguous_project_dir(tmp_path, indicator_file):
    (tmp_path / indicator_file).touch()

    working_dir = tmp_path / "subdir"
    working_dir.mkdir()
    assert str(discover_project_dir(working_dir)) == str(tmp_path)


def test_discovery_skips_setup_py_dir_with_init_py(tmp_path):
    (tmp_path / "pyproject.toml").touch()

    module_dir = tmp_path / "subdir1"
    module_dir.mkdir()

    (module_dir / "setup.py").touch()
    (module_dir / "__init__.py").touch()

    assert str(discover_project_dir(module_dir)) == str(tmp_path)

    # removing the __init__.py changes discovery
    (module_dir / "__init__.py").unlink()
    assert str(discover_project_dir(module_dir)) == str(module_dir)


def test_discovery_selects_setup_py_at_repo_root_as_final_guess(tmp_path):
    # "repo root"
    (tmp_path / "setup.py").touch()
    (tmp_path / ".git").mkdir()
    # but it contains an '__init__.py', so normally it would not be considered
    (tmp_path / "__init__.py").touch()

    subdir = tmp_path / "subdir1"
    subdir.mkdir()

    assert str(discover_project_dir(subdir)) == str(tmp_path)


@pytest.mark.parametrize("vcs_indicator", (".git", ".hg", ".svn"))
def test_discovery_raises_lookup_error_if_no_project_indicator_is_found(
    tmp_path, vcs_indicator
):
    (tmp_path / vcs_indicator).mkdir()

    loc = tmp_path / "subdir"
    loc.mkdir()

    with pytest.raises(LookupError, match="mddj could not find the project root"):
        discover_project_dir(loc)
