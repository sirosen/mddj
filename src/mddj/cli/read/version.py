import click

from mddj.builder import ephemeral_sdist
from mddj.readers import TarballSourceDistribution


@click.command("version")
@click.help_option("-h", "--help")
@click.option(
    "--no-build-capture",
    is_flag=True,
    help="Disable capturing of the internal package build output and errors.",
)
def read_version(*, no_build_capture: bool) -> None:
    """Read the 'Version' of the current project."""
    with ephemeral_sdist(capture_build_output=not no_build_capture) as sdist_path:
        dist = TarballSourceDistribution(sdist_path)
        click.echo(dist.version)
