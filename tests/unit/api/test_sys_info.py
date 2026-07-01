import packaging.markers
import pytest

from mddj.api.reader.system_info import _SystemInfoReaderImplementation


@pytest.fixture
def default_environment():
    return packaging.markers.default_environment()


@pytest.fixture
def sys_reader():
    return _SystemInfoReaderImplementation()


@pytest.mark.parametrize(
    "fieldname",
    (
        "implementation_name",
        "implementation_version",
        "os_name",
        "platform_machine",
        "platform_release",
        "platform_system",
        "platform_version",
        "python_full_version",
        "platform_python_implementation",
        "python_version",
        "sys_platform",
    ),
)
def test_sys_reader_field_matches_packaging_default_env(
    sys_reader, default_environment, fieldname
):
    assert fieldname in default_environment
    assert hasattr(sys_reader, fieldname)
    assert getattr(sys_reader, fieldname)() == default_environment[fieldname]
