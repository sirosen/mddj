import typing as t

import click

from mddj._cli.state import CommandState, common_args


@click.command("authors")
@common_args
@click.option(
    "--only",
    type=click.Choice(("name", "email")),
    help="Only show one field from 'authors' data.",
)
def read_authors(
    *, only: t.Literal["name", "email"] | None, state: CommandState
) -> None:
    """
    Read the "authors" of the current project.

    Note that when dynamic author metadata is encountered, it is not always possible to
    perfectly reconstruct the inputs.
    """
    authors = state.dj.read.authors()

    for author_item in authors:
        if only is not None and only not in author_item:
            continue

        if only == "name":
            click.echo(author_item["name"])
        elif only == "email":
            click.echo(author_item["email"])
        else:
            if {"name", "email"} <= author_item.keys():
                click.echo(f"{author_item['name']} <{author_item['email']}>")
            elif "name" in author_item:
                click.echo(author_item["name"])
            else:
                click.echo(f"<{author_item['email']}>")
