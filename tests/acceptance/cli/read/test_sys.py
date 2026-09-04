import re

import packaging.markers
import pytest

from tests.acceptance.conftest import LineRunner


@pytest.fixture
def default_environment() -> packaging.markers.Environment:
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
    run_line: LineRunner,
    default_environment: packaging.markers.Environment,
    fieldname: str,
) -> None:
    assert fieldname in default_environment
    expected_value = default_environment[fieldname]  # type: ignore[literal-required]

    command_name = fieldname.replace("_", "-")
    run_line(
        f"mddj read sys {command_name}",
        search_stdout=["^" + re.escape(expected_value) + "$"],
    )
