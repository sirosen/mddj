import click

from mddj.cli.state import CommandState, common_args


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
    data = state.read_metadata()
    requires_python = data.get("Requires-Python")

    if requires_python is None or not isinstance(requires_python, str):
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
