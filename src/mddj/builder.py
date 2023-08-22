import contextlib
import pathlib
import subprocess
import sys
import tempfile
import typing as t

import click


@contextlib.contextmanager
def ephemeral_sdist(*, capture_build_output: bool = True) -> t.Iterator[pathlib.Path]:
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.run(
                [sys.executable, "-m", "build", "--sdist", "-o", tmpdir],
                check=True,
                capture_output=capture_build_output,
            )
        except subprocess.CalledProcessError as e:
            if capture_build_output:
                click.secho(
                    "Encountered errors in build. "
                    "Use --no-build-capture to see full details.",
                    fg="red",
                    err=True,
                )
            click.get_current_context().exit(e.returncode)

        # now we have an sdist, so let's find it.
        # the package version will be in the name, so we sniff for any .tar.gz file
        # there will only be one file
        sdist_path = next(pathlib.Path(tmpdir).glob("*.tar.gz"))
        yield sdist_path
