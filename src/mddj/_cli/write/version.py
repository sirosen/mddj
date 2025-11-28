import click

from mddj._cli.state import CommandState, common_args


@click.command("version")
@click.argument("NEW_VERSION")
@common_args
def write_version(*, new_version: str, state: CommandState) -> None:
    """Write the 'version' of the current project, based on config."""
    try:
        result = state.dj.write.version(new_version)
    except LookupError as e:
        click.echo(str(e))
        click.get_current_context().exit(1)
    click.echo(
        f"""\
Version was updated. write_version='{state.dj.write.config.write_version}'

old value: {result}
new value: {new_version}
"""
    )
