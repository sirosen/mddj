import pathlib

import pytest
from packaging.version import Version

# for some reason, mypy flags 'loads' as not explicitly exported
from ryaml import loads as _ryaml_loads  # type: ignore[attr-defined]

from mddj.api import DJ


@pytest.fixture(scope="session")
def dj() -> DJ:
    return DJ()


@pytest.fixture(scope="session")
def requires_python(dj: DJ) -> Version:
    value = dj.read.requires_python(lower_bound=True)
    assert value
    return Version(value)


@pytest.fixture(scope="session")
def ci_workflow_content() -> str:
    root = pathlib.Path(__file__).parent.parent.parent
    path = root / ".github" / "workflows" / "build.yaml"
    return path.read_text()


@pytest.fixture(scope="session")
def all_ci_python_versions(ci_workflow_content: str) -> frozenset[str]:
    pythons = set()

    body = _ryaml_loads(ci_workflow_content)
    jobs = body["jobs"].values()
    for job in jobs:
        if "strategy" in job and "matrix" in job["strategy"]:
            matrix = job["strategy"]["matrix"]
            if isinstance(py_value := matrix.get("py"), list):
                pythons.update(py_value)
            for item in matrix.get("include", []):
                if isinstance(py_value := item.get("py"), str):
                    pythons.add(py_value)

    return frozenset(pythons)


def test_classifiers_are_in_bounds(requires_python: Version, dj: DJ) -> None:
    classifier_versions = [
        Version(v) for v in dj.read.classifiers(python_versions=True)
    ]
    min_classifier_version = min(classifier_versions)
    assert min_classifier_version >= requires_python


def test_readthedocs_version_is_in_bounds(requires_python: Version, dj: DJ) -> None:
    rtd_version = Version(dj.read.readthedocs.python_version())
    assert rtd_version >= requires_python


def test_min_tox_version_matches_requires_python(
    requires_python: Version, dj: DJ
) -> None:
    tox_min_version = Version(dj.read.tox.min_python_version())
    assert tox_min_version == requires_python


def test_min_ci_python_version_matches_requires_python(
    all_ci_python_versions: frozenset[str], requires_python: Version
) -> None:
    min_ci_version = min(Version(v) for v in all_ci_python_versions if v != "3.x")
    assert min_ci_version == requires_python
