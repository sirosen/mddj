import typing as t

import click
from packaging.version import Version

from mddj._cli.state import CommandState, common_args


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
    version = state.dj.read.version()
    if attr is not None:
        version = _get_version_attr(version, attr)
    click.echo(version)


def _get_version_attr(
    version: str, attr: t.Literal["release", "major", "minor", "micro", "pre", "post"]
) -> str:
    parsed_version = Version(version)

    if attr == "release":
        return ".".join(str(n) for n in parsed_version.release)
    elif attr == "major":
        return str(parsed_version.major)
    elif attr == "minor":
        return str(parsed_version.minor)
    elif attr == "micro":
        return str(parsed_version.micro)
    elif attr == "pre":
        if not parsed_version.is_prerelease:
            click.echo(f"'{version}' is not a prerelease", err=True)
            click.get_current_context().exit(1)
        pre_parts: tuple[str | int, ...] = (
            parsed_version.pre  # type: ignore[assignment]
        )
        return "".join(str(n) for n in pre_parts)
    elif attr == "post":
        if not parsed_version.is_postrelease:
            click.echo(f"'{version}' is not a post-release", err=True)
            click.get_current_context().exit(1)
        return str(parsed_version.post)
    else:
        t.assert_never(attr)
