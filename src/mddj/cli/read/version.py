import click

from mddj.cli.state import CommandState, common_args
from mddj.config import ReadVersionSetting
from mddj.readers import read_pyproject_toml_value


@click.command("version")
@common_args
def read_version(*, state: CommandState) -> None:
    """Read the 'Version' of the current project."""
    config = state.read_config()

    if config.read_version_setting == ReadVersionSetting.pyproject:
        try:
            version: str = str(
                read_pyproject_toml_value(state.pyproject_path, "project", "version")
            )
        except LookupError:
            click.echo(
                "No version was found in pyproject.toml:project.version.", err=True
            )
            click.get_current_context().exit(1)
    elif config.read_version_setting == ReadVersionSetting.build:
        data = state.read_metadata()
        version = data.get("Version")
    else:
        raise NotImplementedError(
            "'mddj read version' is missing support for "
            f"read_version={config.read_version_setting!r}"
        )

    click.echo(version)
