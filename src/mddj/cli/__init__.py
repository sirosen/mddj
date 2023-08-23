import click

from .read import read


@click.group("mddj")
@click.help_option("-h", "--help")
def main() -> None:
    """MetaData DJ"""


main.add_command(read)
