import click

from mddj._cli.state import CommandState, common_args


@click.command("requires-python")
@click.argument("REQUIRES_PYTHON")
@click.option(
    "--verbatim",
    is_flag=True,
    help=(
        "Write an exact expression to the requires-python field. "
        "By default, the input is treated as a lower bound."
    ),
)
@common_args
def write_requires_python(
    *, requires_python: str, verbatim: bool, state: CommandState
) -> None:
    """Write the 'requires-python' of the current project in `pyproject.toml`."""
    try:
        result = state.dj.write.requires_python(requires_python, verbatim=verbatim)
    except (LookupError, ValueError) as e:
        click.echo(str(e))
        click.get_current_context().exit(1)

    new_value = requires_python if verbatim else f">={requires_python}"

    click.echo(f"""\
Requires-Python was updated.

old value: {result}
new value: {new_value}
""")
