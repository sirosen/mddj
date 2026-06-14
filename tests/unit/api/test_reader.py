from textwrap import dedent as d
from unittest import mock

import pytest

from mddj._internal import _cached_toml
from mddj.api.discovery import DirExplorer
from mddj.api.reader import _config as _reader_config
from mddj.api.reader import _ReaderImplementation
from mddj.api.reader.dynamic_package import DynamicPackageReader


def _make_reader(config):
    return _ReaderImplementation(config, _cached_toml.TomlDocumentCache())


def make_fake_package_metadata(
    name="foo",
    version="0.0.1",
    summary="the foo pkg",
    keywords="networking,cli,big data",
    requires_python=">= 3.7",
    requires_dist=("bar", "baz", "colorama; extra == 'cli'"),
    provides_extra=("cli",),
):
    fake = mock.Mock()
    fake._data = {
        "Name": name,
        "Version": version,
        "Summary": summary,
        "Keywords": keywords,
        "Requires-Python": requires_python,
        "Requires-Dist": requires_dist,
        "Provides-Extra": provides_extra,
    }

    def get(key):
        value = fake._data.get(key)
        if value is not None and not isinstance(value, str):
            pytest.fail(f"bad get() usage on key: {key}")
        return value

    fake.get.side_effect = get

    def get_all(key, failobj=None):
        value = fake._data.get(key, failobj)
        if value is failobj:
            return failobj
        if value is not None and not isinstance(value, tuple):
            pytest.fail(f"bad get_all() usage on key: {key}")
        return value

    fake.get_all.side_effect = get_all

    return fake


@pytest.fixture
def pyproject_path(tmp_path):
    return tmp_path / "pyproject.toml"


@pytest.fixture
def reader_config(tmp_path, chdir):
    with chdir(tmp_path):
        yield _reader_config.ReaderConfig(
            dir_explorer=DirExplorer(tmp_path),
            project_directory=None,
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
    pyproject_path,
    reader_config,
    monkeypatch,
    read_method,
    pyproject_fieldname,
    toml_value,
    expect_result,
):
    pyproject_path.write_text(
        d(f"""\
            [project]
            {pyproject_fieldname} = {toml_value}
            """),
        encoding="utf-8",
    )

    reader = _make_reader(reader_config)

    # replace the *descriptor*, not the instance value
    monkeypatch.setattr(
        DynamicPackageReader, "_wheel_package_metadata", make_fake_package_metadata()
    )

    method = getattr(reader, read_method)
    assert method() == expect_result


def test_metadata_reader_pulls_dynamic_dependencies_and_handles_extras(
    pyproject_path, reader_config, monkeypatch
):
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
        "_wheel_package_metadata",
        make_fake_package_metadata(
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
