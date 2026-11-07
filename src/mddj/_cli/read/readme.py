import click

from mddj._cli.state import CommandState, common_args


@click.command("readme")
@click.option(
    "--content",
    is_flag=True,
    help=(
        "Show the readme contents and no other fields. "
        "By default, the readme descriptive data is extracted and formatted."
    ),
)
@common_args
def read_readme(*, state: CommandState, content: bool) -> None:
    """
    Read the 'readme' / 'Description' data.

    When `--content` is given, this command only prints the text content of the readme.
    Otherwise, the readme table (`pyproject.toml`) or Description-Content-Type
    (metadata) fields are used to construct readme properties to display.
    """
    readme = state.dj.read.readme(content=content)
    if content:
        click.echo(readme)
    else:
        if readme is None:
            click.echo("no readme", err=True)
        elif isinstance(readme, str):
            click.echo(readme)
        else:
            keys = sorted(k for k in readme if k != "text")
            if keys:
                fill_width = max(len(k) for k in keys) + 1
                for key in keys:
                    prefix = f"{key}:".ljust(fill_width)
                    click.echo(f"{prefix} {readme[key]}")
            if "text" in readme:
                click.echo("text:\n")
                click.echo(readme["text"])
