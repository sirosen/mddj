import click
from packaging.version import Version

from mddj.cli.state import CommandState, common_args
from mddj.readers import get_tox_tested_versions


@click.command("list-versions")
@common_args
def tox_list_versions(*, state: CommandState) -> None:
    """Print all of the python versions tested under tox in version-sorted order."""
    versions = get_tox_tested_versions()
    for v in sorted(Version(v) for v in versions):
        click.echo(str(v))
