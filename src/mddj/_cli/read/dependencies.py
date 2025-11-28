import pathlib

import click

from mddj._cli.state import CommandState, common_args
from mddj._internal import _readers
from mddj._internal._types import is_toml_array


@click.command("dependencies")
@common_args
def read_dependencies(*, state: CommandState) -> None:
    """Read the dependencies of the current project."""
    # first, try reading from pyproject.toml
    dependencies: list[str] | None = _get_dependencies_pyproject(state.pyproject_path)

    # if that fails, fallback to trying to read from build metadata
    if dependencies is None:
        dependencies = _get_dependencies_build(state)

    for d in dependencies:
        click.echo(d)


def _get_dependencies_pyproject(pyproject_path: pathlib.Path) -> list[str] | None:
    try:
        value = _readers.read_pyproject_toml_value(
            pyproject_path, "project", "dependencies"
        )
    except (FileNotFoundError, LookupError):
        return None

    if is_toml_array(value):
        return [str(d) for d in value]

    raise ValueError("Unexpected type for [project.dependencies], could not read")


def _get_dependencies_build(state: CommandState) -> list[str]:
    data = state.read_metadata()
    value = data.get_all("Requires-Dist")
    return [str(d) for d in value]
