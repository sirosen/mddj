import pathlib
import typing as t
from textwrap import dedent as d
from unittest import mock

import pytest

from mddj._internal import _cached_toml, _discovery, _wheel_metadata
from mddj.api.reader._config import ReaderConfig
from mddj.api.reader._main_reader import _ReaderImplementation
from mddj.api.reader.dynamic_package import DynamicPackageReader
from tests.types import ChdirType


def _make_reader(config: ReaderConfig) -> _ReaderImplementation:
    return _ReaderImplementation(config)


class FakeEntryPoint(t.NamedTuple):
    group: str
    name: str
    value: str


def make_fake_wheel_info(
    name: str = "foo",
    version: str = "0.0.1",
    summary: str = "the foo pkg",
    keywords: str = "networking,cli,big data",
    requires_python: str = ">= 3.7",
    requires_dist: tuple[str, ...] = ("bar", "baz", "colorama; extra == 'cli'"),
    provides_extra: tuple[str, ...] = ("cli",),
    entry_points: tuple[FakeEntryPoint, ...] = (),
) -> t.Any:
    fake_meta = mock.Mock()
    fake_meta._data = {
        "Name": name,
        "Version": version,
        "Summary": summary,
        "Keywords": keywords,
        "Requires-Python": requires_python,
        "Requires-Dist": requires_dist,
        "Provides-Extra": provides_extra,
    }

    def get(key: str) -> str | None:
        value = fake_meta._data.get(key)
        if value is not None and not isinstance(value, str):
            pytest.fail(f"bad get() usage on key: {key}")
        return value

    fake_meta.get.side_effect = get

    def get_all(key: str, failobj: t.Any = None) -> t.Any:
        value = fake_meta._data.get(key, failobj)
        if value is failobj:
            return failobj
        if value is not None and not isinstance(value, tuple):
            pytest.fail(f"bad get_all() usage on key: {key}")
        return value

    fake_meta.get_all.side_effect = get_all

    def ep_select(*, group):
        return [ep for ep in entry_points if ep.group == group]

    fake_eps = mock.Mock()
    fake_eps.groups = list({ep.group for ep in entry_points})
    fake_eps.select = ep_select

    fake_info = mock.Mock()
    fake_info.metadata = fake_meta
    fake_info.entry_points = fake_eps
    fake_info.dependency_data = _wheel_metadata.load_wheel_dependency_data(fake_meta)

    return fake_info


@pytest.fixture
def pyproject_path(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "pyproject.toml"


@pytest.fixture
def reader_config(tmp_path: pathlib.Path, chdir: ChdirType) -> t.Iterator[ReaderConfig]:
    with chdir(tmp_path):
        yield _ReaderImplementation._ConfigClass(
            dir_explorer=_discovery.DirExplorer(tmp_path),
            document_cache=_cached_toml.TomlDocumentCache(),
            isolated_builds=True,
            capture_build_output=True,
        )


@pytest.mark.parametrize(
    (
        "read_method",
        "pyproject_fieldname",
        "toml_value",
        "expect_result",
    ),
    [
        ("name", "name", '"foopkg"', "foopkg"),
        ("version", "version", '"1.1"', "1.1"),
        ("description", "description", '"such a cool package"', "such a cool package"),
        ("keywords", "keywords", '["cli"]', ("cli",)),
        ("requires_python", "requires-python", '">= 3.6.2"', ">= 3.6.2"),
        ("dependencies", "dependencies", '["barlib"]', ("barlib",)),
    ],
)
def test_metadata_reader_prefers_fields_from_static_metadata(
    pyproject_path: pathlib.Path,
    reader_config: ReaderConfig,
    monkeypatch: pytest.MonkeyPatch,
    read_method: str,
    pyproject_fieldname: str,
    toml_value: str,
    expect_result: str | tuple[str, ...],
) -> None:
    pyproject_path.write_text(
        d(f"""\
            [project]
            {pyproject_fieldname} = {toml_value}
            """),
        encoding="utf-8",
    )

    reader = _make_reader(reader_config)

    # replace the *descriptor*, not the instance value
    monkeypatch.setattr(DynamicPackageReader, "_wheel_info", make_fake_wheel_info())

    method = getattr(reader, read_method)
    assert method() == expect_result


def test_metadata_reader_pulls_dynamic_dependencies_and_handles_extras(
    pyproject_path: pathlib.Path,
    reader_config: ReaderConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pyproject_path.write_text(
        d("""\
            [project]
            dynamic = [
                "name", "version", "description", "keywords", "requires-python",
                "dependencies", "optional-dependencies"
            ]
            """),
        encoding="utf-8",
    )

    reader = _make_reader(reader_config)

    # replace the *descriptor*, not the instance value
    monkeypatch.setattr(
        DynamicPackageReader,
        "_wheel_info",
        make_fake_wheel_info(
            requires_dist=(
                "bar",
                "baz",
                "colorama; extra == 'cli'",
                "better-tracebacks; extra == 'cli'",
                "better-tracebacks; extra == 'pretty'",
            ),
            provides_extra=("cli", "pretty"),
        ),
    )

    # dependencies should only show `bar` and `baz` -- the others "look optional"
    assert reader.dependencies() == ("bar", "baz")

    # optional deps should strip all of the extra markers by default
    extras_cleaned = reader.optional_dependencies()
    assert set(extras_cleaned.keys()) == {"cli", "pretty"}
    assert set(extras_cleaned["cli"]) == {"colorama", "better-tracebacks"}
    assert set(extras_cleaned["pretty"]) == {"better-tracebacks"}

    # but with the arg to preserve exact, we get the "ugly" true data
    extras_exact = reader.optional_dependencies(exact_wheel_metadata=True)
    assert set(extras_exact.keys()) == {"cli", "pretty"}
    assert set(extras_exact["cli"]) == {
        "colorama; extra == 'cli'",
        "better-tracebacks; extra == 'cli'",
    }
    assert set(extras_exact["pretty"]) == {"better-tracebacks; extra == 'pretty'"}


def test_metadata_reader_prefers_static_entry_points_data(
    pyproject_path: pathlib.Path,
    reader_config: ReaderConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pyproject_path.write_text(
        d("""\
            [project]
            name = "foo"
            version = "0.1"

            [project.scripts]
            foo-cli = 'foo.main:cli'
            """),
        encoding="utf-8",
    )

    reader = _make_reader(reader_config)

    # replace the *descriptor*, not the instance value
    monkeypatch.setattr(
        DynamicPackageReader,
        "_wheel_info",
        make_fake_wheel_info(
            # note that this is intentionally a little different from the static data
            # given above
            entry_points=(
                FakeEntryPoint("console_scripts", "foo-bar-cli", "foo.main:main"),
            ),
        ),
    )

    # act! (load the data)
    eps = reader.entry_points()

    # assert:
    # - the keys are console_scripts
    # - there is only one value
    # - that value maps 'foo-cli' to 'foo.main:cli' (static data)
    # - we can also get the dynamic data explicitly
    assert list(eps) == ["console_scripts"]
    assert tuple(eps["console_scripts"].items()) == (("foo-cli", "foo.main:cli"),)

    dynamic_eps = reader.dynamic.entry_points()
    assert list(dynamic_eps) == ["console_scripts"]
    assert tuple(dynamic_eps["console_scripts"].items()) == (
        ("foo-bar-cli", "foo.main:main"),
    )


def test_metadata_reader_falls_back_to_dynamic_entry_points_data(
    pyproject_path: pathlib.Path,
    reader_config: ReaderConfig,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pyproject_path.write_text(
        d("""\
            [project]
            name = "foo"
            version = "0.1"
            """),
        encoding="utf-8",
    )

    reader = _make_reader(reader_config)

    # replace the *descriptor*, not the instance value
    monkeypatch.setattr(
        DynamicPackageReader,
        "_wheel_info",
        make_fake_wheel_info(
            entry_points=(
                FakeEntryPoint("console_scripts", "foo-cli", "foo.main:cli"),
            ),
        ),
    )

    # act! (load the data)
    eps = reader.entry_points()

    # assert:
    # - the keys are console_scripts
    # - there is only one value
    # - that value maps 'foo-cli' to 'foo.main:cli'
    assert list(eps) == ["console_scripts"]
    assert tuple(eps["console_scripts"].items()) == (("foo-cli", "foo.main:cli"),)
