import click
from packaging.utils import canonicalize_name

from mddj._cli.state import CommandState, common_args


def _normalize_extra_callback(
    ctx: click.Context, param: click.Parameter, value: str | None
) -> str | None:
    if not value:
        return value
    return canonicalize_name(value, validate=True)


@click.command("optional-dependencies")
@common_args
@click.option(
    "--extra",
    help=(
        "Only read this extra name. If the project does not "
        "define such an extra, exit with an error."
    ),
    callback=_normalize_extra_callback,
)
@click.option(
    "--exact-wheel-metadata",
    help=(
        "Disable cleanup of the markers on optional dependencies when optional "
        "dependencies are dynamic and a wheel build is needed."
    ),
    is_flag=True,
)
def read_optional_dependencies(
    *,
    extra: str | None,
    exact_wheel_metadata: bool,
    state: CommandState,
) -> None:
    """
    Read the optional dependencies or "extras" of the current project.

    By default, all optional dependencies are shown, grouped by their extra name.
    If an extra name is given, only the optional dependencies for that extra will be
    shown.

    When optional dependencies are dynamic, users may be surprised that extras are
    encoded into dependency markers. By default, `mddj` will try to strip off these
    modifications. Use `--exact-wheel-metadata` to disable this behavior.
    """
    opt_deps = state.dj.read.optional_dependencies(
        exact_wheel_metadata=exact_wheel_metadata
    )

    if extra:
        if extra not in opt_deps:
            click.echo(
                f"'{extra}' does not appear in project extras. Valid names are:",
                err=True,
            )
            for key in opt_deps.keys():
                click.echo(f"    {key}", err=True)
            click.get_current_context().exit(1)
        for dep in opt_deps[extra]:
            click.echo(dep)
    else:
        for extra_name, deps in opt_deps.items():
            click.echo(f"{extra_name}:")
            for dep in deps:
                click.echo(f"    {dep}")
