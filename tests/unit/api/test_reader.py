from textwrap import dedent as d
from unittest import mock

import pytest

from mddj.api.config import ReaderConfig
from mddj.api.reader import Reader


def make_fake_package_metadata(
    name="foo",
    version="0.0.1",
    summary="the foo pkg",
    keywords="networking,cli,big data",
    requires_python=">= 3.7",
    requires_dist=("bar", "baz"),
):
    fake = mock.Mock()
    fake._data = {
        "Name": name,
        "Version": version,
        "Summary": summary,
        "Keywords": keywords,
        "Requires-Python": requires_python,
        "Requires-Dist": requires_dist,
    }

    def get(key):
        value = fake._data.get(key)
        if value is not None and not isinstance(value, str):
            pytest.fail(f"bad get() usage on key: {key}")
        return value

    fake.get.side_effect = get

    def get_all(key):
        value = fake._data.get(key)
        if value is not None and not isinstance(value, tuple):
            pytest.fail(f"bad get_all() usage on key: {key}")
        return value

    fake.get_all.side_effect = get_all

    return fake


@pytest.fixture
def reader_config(tmp_path, chdir):
    pyproject_path = tmp_path / "pyproject.toml"

    with chdir(tmp_path):
        yield ReaderConfig(
            pyproject_path=pyproject_path,
            project_directory=tmp_path,
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
    reader_config,
    monkeypatch,
    read_method,
    pyproject_fieldname,
    toml_value,
    expect_result,
):
    reader_config.pyproject_path.write_text(
        d(
            f"""\
            [project]
            {pyproject_fieldname} = {toml_value}
            """
        ),
        encoding="utf-8",
    )

    reader = Reader(reader_config)

    # replace the *descriptor*, not the instance value
    monkeypatch.setattr(Reader, "_wheel_metadata", make_fake_package_metadata())

    method = getattr(reader, read_method)
    assert method() == expect_result
