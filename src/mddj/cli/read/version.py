import pathlib

import click

from mddj.cli.state import CommandState, common_args
from mddj.readers import read_pyproject_toml_value


@click.command("version")
@common_args
def read_version(*, state: CommandState) -> None:
    """Read the 'Version' of the current project."""
    # first, try reading from pyproject.toml
    version: str | None = _get_version_pyproject(state.pyproject_path)

    # if that fails, fallback to trying to read from build metadata
    if version is None:
        version = _get_version_build(state)

    click.echo(version)


def _get_version_pyproject(pyproject_path: pathlib.Path) -> str | None:
    try:
        return str(read_pyproject_toml_value(pyproject_path, "project", "version"))
    except (FileNotFoundError, LookupError):
        return None


def _get_version_build(state: CommandState) -> str:
    data = state.read_metadata()
    return str(data.get("Version"))
