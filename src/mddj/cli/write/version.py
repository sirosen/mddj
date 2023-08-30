import click

from mddj.cli.state import CommandState, common_args
from mddj.config import WriteVersionAssignConfig
from mddj.writers import write_simple_assignment


@click.command("version")
@click.argument("NEW_VERSION")
@common_args
def write_version(*, new_version: str, state: CommandState) -> None:
    """Write the 'version' of the current project, based on config."""
    config = state.read_config()
    version_config = config.write_version_config
    if isinstance(version_config, WriteVersionAssignConfig):
        result = write_simple_assignment(
            version_config.path, version_config.key, new_version
        )
    else:
        raise NotImplementedError(
            f"Unrecognized write_version_config. write_version={config.write_version}"
        )

    if result is None:
        click.echo("No version was found, so no update was written.")
        click.get_current_context().exit(1)
    else:
        click.echo(
            f"""\
Version was updated. write_version='{config.write_version}'

old value: {result}
new value: {new_version}
"""
        )
