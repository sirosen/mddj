import pathlib

import click

from mddj.cli.state import CommandState, common_args
from mddj.readers import read_pyproject_toml_value


@click.command("requires-python")
@click.option(
    "--lower-bound",
    is_flag=True,
    help="Show a lower bound rather than the full Requires-Python data.",
)
@common_args
def read_requires_python(*, state: CommandState, lower_bound: bool) -> None:
    """
    Read the 'Requires-Python' data.
    """
    # first, try reading from pyproject.toml
    requires_python = _get_requires_python_pyproject(state.pyproject_path)

    # if that fails, fallback to trying to read from build metadata
    if requires_python is None:
        requires_python = _get_requires_python_build(state)

    if requires_python is None:
        raise RuntimeError("No Requires-Python data found")

    if lower_bound:
        click.echo(find_lower_bound(requires_python))
    else:
        click.echo(requires_python)


def find_lower_bound(req: str) -> str:
    reqs = req.split(",")
    lower_bounds = []
    for r in reqs:
        if r.startswith(">="):
            lower_bounds.append(r[2:])
        elif r.startswith(">"):
            raise RuntimeError(
                "Found a > requirement, rejecting as invalid (use '>=' instead)"
            )
    if len(lower_bounds) > 1:
        raise RuntimeError("Found multiple lower bounds, cannot choose one")
    elif len(lower_bounds) == 0:
        raise RuntimeError("Found no lower bounds")
    else:
        return lower_bounds[0]


def _get_requires_python_pyproject(pyproject_path: pathlib.Path) -> str | None:
    try:
        return str(
            read_pyproject_toml_value(pyproject_path, "project", "requires-python")
        )
    except (FileNotFoundError, LookupError):
        return None


def _get_requires_python_build(state: CommandState) -> str | None:
    data = state.read_metadata()
    value = data.get("Requires-Python")
    if value is None:
        return None
    return str(value)
