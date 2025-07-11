import pathlib
import typing as t

import click
from packaging.version import Version

from mddj.cli.state import CommandState, common_args
from mddj.readers import read_pyproject_toml_value


@click.command("version")
@common_args
@click.option(
    "--attr",
    help=(
        "Read an attribute of the version, not the whole version number. "
        "If 'pre' or 'post' is used and the release is not a prerelease or "
        "post-release, the command will exit(1) with an error."
    ),
    type=click.Choice(
        ("release", "major", "minor", "micro", "pre", "post"), case_sensitive=False
    ),
)
def read_version(
    *,
    attr: t.Literal["release", "major", "minor", "micro", "pre", "post"] | None,
    state: CommandState,
) -> None:
    """Read the 'Version' of the current project."""
    # first, try reading from pyproject.toml
    version: str | None = _get_version_pyproject(state.pyproject_path)

    # if that fails, fallback to trying to read from build metadata
    if version is None:
        version = _get_version_build(state)

    if attr is None:
        click.echo(version)
    else:
        parsed_version = Version(version)
        if attr == "release":
            click.echo(".".join(str(n) for n in parsed_version.release))
        elif attr == "major":
            click.echo(parsed_version.major)
        elif attr == "minor":
            click.echo(parsed_version.minor)
        elif attr == "micro":
            click.echo(parsed_version.micro)
        elif attr == "pre":
            if not parsed_version.is_prerelease:
                click.echo(f"'{version}' is not a prerelease", err=True)
                click.get_current_context().exit(1)
            pre_parts: tuple[str | int, ...] = (
                parsed_version.pre  # type: ignore[assignment]
            )
            click.echo("".join(str(n) for n in pre_parts))
        elif attr == "post":
            if not parsed_version.is_postrelease:
                click.echo(f"'{version}' is not a post-release", err=True)
                click.get_current_context().exit(1)
            click.echo(parsed_version.post)
        else:
            t.assert_never(attr)


def _get_version_pyproject(pyproject_path: pathlib.Path) -> str | None:
    try:
        return str(read_pyproject_toml_value(pyproject_path, "project", "version"))
    except (FileNotFoundError, LookupError):
        return None


def _get_version_build(state: CommandState) -> str:
    data = state.read_metadata()
    return str(data.get("Version"))
