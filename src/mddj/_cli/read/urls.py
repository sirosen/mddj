import click

from mddj._cli.state import CommandState, common_args


@click.command("urls")
@click.option("--normalize", is_flag=True, help="Normalize the URL keys.")
@click.option("--name", help="Fetch the value for a given URL name.")
@common_args
def read_urls(*, state: CommandState, normalize: bool, name: str | None) -> None:
    """
    Read the Project URLs.

    `--name` can be used to fetch a specific URL, especially when combined with
    `--normalize`. For example:

        mddj read urls --normalize --name changelog
    """
    urls = state.dj.read.urls(normalize=normalize)
    if not urls:
        click.echo("no url data found", err=True)
        click.get_current_context().exit(0)

    if name:
        if name not in urls:
            click.echo(f"name {name!r} was not found in urls", err=True)
            click.get_current_context().exit(1)
        click.echo(urls[name].strip())
    else:
        for key, value in urls.items():
            click.echo(f"{key.strip()} = {value.strip()}")
