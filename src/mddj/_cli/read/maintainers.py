import typing as t

import click

from mddj._cli.state import CommandState, common_args


@click.command("maintainers")
@common_args
@click.option(
    "--only",
    type=click.Choice(("name", "email")),
    help="Only show one field from 'maintainers' data.",
)
def read_maintainers(
    *, only: t.Literal["name", "email"] | None, state: CommandState
) -> None:
    """
    Read the "maintainers" of the current project.

    Note that when dynamic maintainer metadata is encountered, it is not always possible
    to perfectly reconstruct the inputs.
    """
    maintainers = state.dj.read.maintainers()

    for maintainer_item in maintainers:
        if only is not None and only not in maintainer_item:
            continue

        if only == "name":
            click.echo(maintainer_item["name"])
        elif only == "email":
            click.echo(maintainer_item["email"])
        else:
            if {"name", "email"} <= maintainer_item.keys():
                click.echo(f"{maintainer_item['name']} <{maintainer_item['email']}>")
            elif "name" in maintainer_item:
                click.echo(maintainer_item["name"])
            else:
                click.echo(f"<{maintainer_item['email']}>")
