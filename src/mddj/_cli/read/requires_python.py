import click

from mddj._cli.state import CommandState, common_args


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
    requires_python = state.dj.read.requires_python(lower_bound=lower_bound)
    click.echo(requires_python)
