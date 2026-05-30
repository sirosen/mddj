import click

from mddj._cli.state import CommandState, common_args


@click.group("readthedocs")
@common_args
def read_readthedocs(*, state: CommandState) -> None:
    """
    Read information from ReadTheDocs configuration.
    """


@read_readthedocs.command("python-version")
@common_args
def python_version(*, state: CommandState) -> None:
    """
    Extract a Python version number from ReadTheDocs configuration.

    By default, this attempts to read from 'build.tools.python'.
    The lookup behavior can be configured in `[tool.mddj.readthedocs]`.
    """
    value = state.dj.read.readthedocs.python_version()
    click.echo(value)
