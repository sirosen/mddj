import pathlib

import click

from mddj.cli.state import CommandState, common_args
from mddj.readers import read_pyproject_toml_value


@click.command("dependencies")
@common_args
def read_dependencies(*, state: CommandState) -> None:
    """Read the dependencies of the current project."""
    # first, try reading from pyproject.toml
    dependencies: str | None = _get_dependencies_pyproject(state.pyproject_path)

    # if that fails, fallback to trying to read from build metadata
    if dependencies is None:
        dependencies = _get_dependencies_build(state)

    for d in dependencies:
        click.echo(d)


def _get_dependencies_pyproject(pyproject_path: pathlib.Path) -> list[str] | None:
    try:
        return [
            str(d)
            for d in read_pyproject_toml_value(
                pyproject_path, "project", "dependencies"
            )
        ]
    except (FileNotFoundError, LookupError):
        return None


def _get_dependencies_build(state: CommandState) -> list[str]:
    data = state.read_metadata()
    return data.get_all("Requires-Dist")
