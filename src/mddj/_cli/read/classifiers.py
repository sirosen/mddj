import click

from mddj._cli.state import CommandState, common_args


@click.command("classifiers")
@click.option(
    "--python-versions",
    is_flag=True,
    help=(
        "Show only the python versions extracted from classifiers, "
        "limited only to versions of the form MAJOR.MINOR."
    ),
)
@common_args
def read_classifiers(*, state: CommandState, python_versions: bool) -> None:
    """Read the classifiers of the current project."""
    for c in state.dj.read.classifiers(python_versions=python_versions):
        click.echo(c)
