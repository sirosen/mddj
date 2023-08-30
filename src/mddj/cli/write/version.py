import click

from mddj.cli.state import CommandState, common_args
from mddj.writers import write_simple_assignment


@click.command("version")
@click.argument("NEW_VERSION")
@common_args
def write_version(*, new_version: str, state: CommandState) -> None:
    """Write the 'version' of the current project, based on config."""
    config = state.read_config()
    if config.write_version_mode == "assign":
        maybe_result = write_simple_assignment(
            config.version_path,
            config.write_version_value,
            new_version,
        )
    else:
        raise NotImplementedError(
            f"Unrecognized write_version_mode: {config.write_version_mode}"
        )

    if maybe_result is None:
        click.echo("No version was found, so no update was written.")
    else:
        click.echo(
            f"""\
Version was updated. write_version={config.write_version}

old value: {maybe_result}
new value: {new_version}
"""
        )