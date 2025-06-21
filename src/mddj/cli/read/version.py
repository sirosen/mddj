import pathlib

import click

from mddj.cli.state import CommandState, common_args
from mddj.config import ReadVersionSetting
from mddj.readers import read_pyproject_toml_value


@click.command("version")
@common_args
def read_version(*, state: CommandState) -> None:
    """Read the 'Version' of the current project."""
    config = state.read_config()

    version: str
    if config.read_version_setting == ReadVersionSetting.default:
        version_pyproj = _get_version_pyproject(state.pyproject_path)
        if version_pyproj is None:
            version = _get_version_build(state)
        else:
            version = version_pyproj

    elif config.read_version_setting == ReadVersionSetting.pyproject:
        version_pyproj = _get_version_pyproject(state.pyproject_path)
        if version_pyproj is None:
            click.echo(
                "No version was found in pyproject.toml:project.version.", err=True
            )
            click.get_current_context().exit(1)
        else:
            version = version_pyproj

    elif config.read_version_setting == ReadVersionSetting.build:
        version = _get_version_build(state)

    else:
        raise NotImplementedError(
            "'mddj read version' is missing support for "
            f"read_version={config.read_version_setting!r}"
        )

    click.echo(version)


def _get_version_pyproject(pyproject_path: pathlib.Path) -> str | None:
    try:
        return str(read_pyproject_toml_value(pyproject_path, "project", "version"))
    except (FileNotFoundError, LookupError):
        return None


def _get_version_build(state: CommandState) -> str:
    data = state.read_metadata()
    return str(data.get("Version"))
