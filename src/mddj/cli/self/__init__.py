import click

from mddj.cli.state import CommandState, common_args

from .version import self_version


@click.group("self")
@common_args
def self(*, state: CommandState) -> None:
    """Interact with mddj itself."""


self.add_command(self_version)
