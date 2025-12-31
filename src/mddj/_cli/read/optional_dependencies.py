import click

from mddj._cli.state import CommandState, common_args


@click.command("optional-dependencies")
@common_args
@click.option("--extra", help="Only read this extra name.")
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
    extra: str,
    exact_wheel_metadata: bool,
    state: CommandState,
) -> None:
    """
    Read the optional dependencies or "extras" of the current project.

    By default, all optional dependencies are shown, grouped by their extra name.
    If an extra name is given, only the optional dependencies for that extra will be
    shown.

    Empty extras are treated valid if the package defines them, but extras which don't
    match package data are treated as errors.

    When optional dependencies are dynamic, users may be surprised that extras are
    encoded into dependency markers. By default, `mddj` will try to strip off these
    modifications. Use `--exact-wheel-metadata` to disable this behavior.
    """
    opt_deps = state.dj.read.optional_dependencies(
        exact_wheel_metadata=exact_wheel_metadata
    )

    if extra:
        if extra not in opt_deps:
            click.echo(f"'{extra}' does not appear in package extras", err=True)
            click.get_current_context().exit(1)
        for dep in opt_deps[extra]:
            click.echo(dep)
    else:
        for extra_name, deps in opt_deps.items():
            click.echo(f"{extra_name}:")
            for dep in deps:
                click.echo(f"    {dep}")
