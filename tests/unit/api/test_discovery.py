import pytest

from mddj.api.discovery import DirExplorer


@pytest.mark.parametrize("indicator_file", ("pyproject.toml", "setup.cfg", "setup.py"))
def test_can_discover_unambiguous_package_dir(tmp_path, indicator_file):
    (tmp_path / indicator_file).touch()

    working_dir = tmp_path / "subdir"
    working_dir.mkdir()

    explorer = DirExplorer(working_dir)
    assert str(explorer.search_for("python-package").dirpath) == str(tmp_path)


def test_discovery_skips_setup_py_dir_with_init_py(tmp_path):
    (tmp_path / "pyproject.toml").touch()

    module_dir = tmp_path / "subdir1"
    module_dir.mkdir()

    (module_dir / "setup.py").touch()
    (module_dir / "__init__.py").touch()

    explorer = DirExplorer(module_dir)
    assert str(explorer.search_for("python-package").dirpath) == str(tmp_path)

    # removing the __init__.py changes discovery (with a fresh explorer)
    (module_dir / "__init__.py").unlink()
    explorer = DirExplorer(module_dir)
    assert str(explorer.search_for("python-package").dirpath) == str(module_dir)


def test_discovery_selects_setup_py_at_repo_root_as_final_guess(tmp_path):
    # "repo root"
    (tmp_path / "setup.py").touch()
    (tmp_path / ".git").mkdir()
    # but it contains an '__init__.py', so normally it would not be considered
    (tmp_path / "__init__.py").touch()

    subdir = tmp_path / "subdir1"
    subdir.mkdir()

    explorer = DirExplorer(subdir)
    assert str(explorer.search_for("python-package").dirpath) == str(tmp_path)


@pytest.mark.parametrize("vcs_indicator", (".git", ".hg", ".svn"))
def test_discovery_raises_lookup_error_if_no_package_indicator_is_found(
    tmp_path, vcs_indicator
):
    (tmp_path / vcs_indicator).mkdir()

    loc = tmp_path / "subdir"
    loc.mkdir()

    explorer = DirExplorer(loc)
    with pytest.raises(
        LookupError,
        match=(
            "mddj searched for a directory which matched the 'python-package' rule "
            "and could not find one."
        ),
    ):
        explorer.search_for("python-package")


@pytest.mark.parametrize("vcs_indicator", (".git", ".hg", ".svn"))
@pytest.mark.parametrize("rtd_filename", (".readthedocs.yaml", ".readthedocs.yml"))
def test_discovery_can_find_readthedocs_without_python_package(
    tmp_path, vcs_indicator, rtd_filename
):
    (tmp_path / vcs_indicator).mkdir()
    (tmp_path / rtd_filename).touch()

    loc = tmp_path / "subdir"
    loc.mkdir()

    explorer = DirExplorer(loc)
    with pytest.raises(LookupError):
        explorer.search_for("python-package")

    assert str(explorer.search_for("readthedocs").dirpath) == str(tmp_path)


@pytest.mark.parametrize("vcs_indicator", (".git", ".hg", ".svn"))
@pytest.mark.parametrize("tox_filename", ("tox.ini", "tox.toml"))
def test_discovery_can_find_tox_without_python_package(
    tmp_path, vcs_indicator, tox_filename
):
    (tmp_path / vcs_indicator).mkdir()
    (tmp_path / tox_filename).touch()

    loc = tmp_path / "subdir"
    loc.mkdir()

    explorer = DirExplorer(loc)
    with pytest.raises(LookupError):
        explorer.search_for("python-package")

    assert str(explorer.search_for("tox").dirpath) == str(tmp_path)
