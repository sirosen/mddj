import types

import click

from mddj._cli.state import CommandState, common_args


@click.command("entry-points")
@click.option(
    "--group",
    help="Limit output to a specific entry point group (and omit the group header).",
)
@common_args
def read_entry_points(*, state: CommandState, group: str | None) -> None:
    """
    Read the Entry Points data.
    """
    eps = state.dj.read.entry_points()
    if group:
        _echo_ep_group(eps, group)
    else:
        first = True
        for group_key in sorted(eps):
            if first:
                first = False
            else:
                click.echo()
            click.echo(f"[{group_key}]")
            _echo_ep_group(eps, group_key)


def _echo_ep_group(
    entry_points: types.MappingProxyType[str, types.MappingProxyType[str, str]],
    group: str,
) -> None:
    for name, value in entry_points[group].items():
        click.echo(f"{name} = {value}")
