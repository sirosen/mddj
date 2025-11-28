import click
from packaging.version import Version

from mddj._cli.state import CommandState, common_args


@click.command("min-version")
@common_args
def tox_min_version(*, state: CommandState) -> None:
    """Print the minimum version of python tested under tox."""
    versions = state.dj.read.tox.list_python_versions()

    if not versions:
        raise RuntimeError("No tox version data found.")
    click.echo(str(sorted(Version(v) for v in versions)[0]))
