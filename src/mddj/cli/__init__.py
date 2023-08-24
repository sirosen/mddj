import click

from .read import read
from .state import CommandState, common_args


@click.group("mddj")
@common_args
def main(*, state: CommandState) -> None:
    """MetaData DJ"""


main.add_command(read)
