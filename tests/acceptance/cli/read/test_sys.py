import re

import packaging.markers
import pytest


@pytest.fixture
def default_environment():
    return packaging.markers.default_environment()


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
def test_sys_reader_command_output_matches_packaging_default_env(
    run_line, default_environment, fieldname
):
    assert fieldname in default_environment
    expected_value = default_environment[fieldname]

    command_name = fieldname.replace("_", "-")
    run_line(
        f"mddj read sys {command_name}",
        search_stdout=["^" + re.escape(expected_value) + "$"],
    )
