import click

from mddj._cli.state import CommandState, common_args


@click.group("sys")
@common_args
def read_sys(*, state: CommandState) -> None:
    """
    Read information about the current system.

    In particular, this provides access to all of the facets which are usable in
    packaging markers.
    """


def _add_command(name: str, base_help: str) -> None:
    command_name = name.replace("_", "-")

    helptext = f"{base_help}\n\nIn Python package markers, this is called '{name}'."

    @read_sys.command(command_name, help=helptext)
    @common_args
    def command(*, state: CommandState) -> None:
        method = getattr(state.dj.read.sys, name)
        click.echo(method())


for name, base_help in (
    ("os_name", "Print the name of the current operating system."),
    ("implementation_name", "Print the name of the current python implementation."),
    (
        "implementation_version",
        "Print the name of the current python implementation version.",
    ),
    (
        "platform_machine",
        (
            "Print the machine type as returned by the operating system, "
            "e.g., 'x86_64', 'aarch64', 'AMD64', or 'arm64'."
        ),
    ),
    (
        "platform_release",
        (
            "Print the system's release, as returned by the operating system.\n\n"
            "On Linux, this will typically match `uname -r`."
        ),
    ),
    (
        "platform_system",
        "Print the system's name, e.g., 'Linux', 'Darwin', or 'Windows'.",
    ),
    ("platform_version", "Print the system's release version."),
    (
        "platform_python_implementation",
        "Print the current Python implementation, e.g., 'cpython' or 'pypy'.",
    ),
    (
        "python_full_version",
        "Print the current Python version, in the format of MAJOR.MINOR.POINT.",
    ),
    (
        "python_version",
        "Print the current Python version, in the format of MAJOR.MINOR.",
    ),
    ("sys_platform", "Print the platform name, e.g., 'linux' or 'win32'."),
):
    _add_command(name, base_help)
