import click
from packaging.version import Version

from mddj._cli.state import CommandState, common_args
from mddj._internal import _readers


@click.command("min-version")
@common_args
def tox_min_version(*, state: CommandState) -> None:
    """Print the minimum version of python tested under tox."""
    versions = _readers.get_tox_tested_versions()

    if not versions:
        raise RuntimeError("No tox version data found.")
    click.echo(str(sorted(Version(v) for v in versions)[0]))
