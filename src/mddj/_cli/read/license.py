import click

from mddj._cli.state import CommandState, common_args


@click.command("license")
@common_args
def read_license(*, state: CommandState) -> None:
    """
    Read the 'license' / 'Description' data.

    When `--content` is given, this command only prints the text content of the license.
    Otherwise, the license table (`pyproject.toml`) or Description-Content-Type
    (metadata) fields are used to construct license properties to display.
    """
    license = state.dj.read.license()
    if license.is_empty:
        click.echo("no license", err=True)
        return

    if license.license_expression:
        click.echo(f"expression: {license.license_expression}")
    if license.license_files:
        click.echo("files:")
        for filename in license.license_files:
            click.echo(f"  - {filename!r}")
    if license.license_text:
        click.echo("text:\n")
        click.echo(license.license_text)
