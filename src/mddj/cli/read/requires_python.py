import click

from mddj.builder import ephemeral_sdist
from mddj.readers import read_from_sdist


@click.command("requires-python")
@click.help_option("-h", "--help")
@click.option(
    "--lower-bound",
    is_flag=True,
    help="Show a lower bound rather than the full Requires-Python data.",
)
@click.option(
    "--no-build-capture",
    is_flag=True,
    help="Disable capturing of the internal package build output and errors.",
)
def read_requires_python(*, lower_bound: bool, no_build_capture: bool) -> None:
    """
    Read the 'Requires-Python' data.
    """
    with ephemeral_sdist(capture_build_output=not no_build_capture) as sdist_path:
        requires_python = read_from_sdist(sdist_path, "Requires-Python")

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
