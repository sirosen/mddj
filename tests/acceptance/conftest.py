import contextlib
import dataclasses
import pathlib
import re
import shlex
import textwrap
import typing as t
from textwrap import dedent as d

import click.testing
import pytest

from tests.types import ChdirType

_PYTEST_VERBOSE = False

_OutputSearchType: t.TypeAlias = (
    str
    | re.Pattern[str]
    | list[str]
    | list[re.Pattern[str]]
    | list[str | re.Pattern[str]]
)


def pytest_configure(config: pytest.Config) -> None:
    if config.getoption("verbose") > 0:
        global _PYTEST_VERBOSE
        _PYTEST_VERBOSE = True


@pytest.fixture
def cli_runner() -> click.testing.CliRunner:
    return click.testing.CliRunner()


class LineRunner:
    def __init__(self, cli_runner: click.testing.CliRunner) -> None:
        self.cli_runner = cli_runner

    def __call__(
        self,
        line: str,
        assert_exit_code: int = 0,
        stdin: str | None = None,
        search_stdout: _OutputSearchType | None = None,
        search_stderr: _OutputSearchType | None = None,
        env: dict[str, str] | None = None,
    ) -> click.testing.Result:
        from mddj._cli import main

        # split line into args and confirm line starts with "mddj"
        args = shlex.split(line) if isinstance(line, str) else line
        assert args[0] == "mddj"

        # run the line. main is the "mddj" part of the line
        # if we are expecting success (0), don't catch any exceptions.
        result = self.cli_runner.invoke(
            main,
            args[1:],
            input=stdin,
            catch_exceptions=bool(assert_exit_code),
            env=env,
        )
        if result.exit_code != assert_exit_code:
            message = d(f"""\
                CliTest run_line exit_code assertion failed!
                Line:
                  {line}
                exited with {result.exit_code} when expecting {assert_exit_code}
                """)
            if _PYTEST_VERBOSE:
                message += (
                    "\n\nstdout:\n"
                    + textwrap.indent(result.stdout, "  ")
                    + "\nstderr:"
                    + textwrap.indent(result.stderr, "  ")
                )

            pytest.fail(message)
        if search_stdout is not None:
            _assert_matches(result.stdout, "stdout", search_stdout)
        if search_stderr is not None:
            _assert_matches(result.stderr, "stderr", search_stderr)
        return result


@pytest.fixture
def run_line(cli_runner: click.testing.CliRunner) -> object:
    return LineRunner(cli_runner)


@dataclasses.dataclass
class CliEnv:
    _chdir: ChdirType
    dir: pathlib.Path
    run_line: LineRunner

    @contextlib.contextmanager
    def chdir(self, path: str | pathlib.Path | None = None) -> t.Iterator[None]:
        with self._chdir(path or self.dir):
            yield

    @property
    def pyproject(self) -> pathlib.Path:
        return self.dir / "pyproject.toml"

    @property
    def setuppy(self) -> pathlib.Path:
        return self.dir / "setup.py"

    @property
    def setupcfg(self) -> pathlib.Path:
        return self.dir / "setup.cfg"


@pytest.fixture
def cli_env(chdir: ChdirType, tmp_path: pathlib.Path, run_line: LineRunner) -> CliEnv:
    return CliEnv(chdir, tmp_path, run_line)


def _assert_matches(text: str, text_name: str, search: _OutputSearchType) -> None:
    __tracebackhide__ = True

    if isinstance(search, (str, re.Pattern)):
        search = [search]
    elif not isinstance(search, list):
        raise NotImplementedError(
            "search_{stdout,stderr} got unexpected arg type: {type(search)}"
        )

    compiled_searches = [
        s if isinstance(s, re.Pattern) else re.compile(s, re.MULTILINE) for s in search
    ]
    for pattern in compiled_searches:
        if pattern.search(text) is None:
            if _PYTEST_VERBOSE:
                pytest.fail(
                    f"Pattern('{pattern.pattern}') not found in {text_name}.\n"
                    f"Full text:\n\n{text}"
                )
            else:
                pytest.fail(
                    f"Pattern('{pattern.pattern}') not found in {text_name}. "
                    "Use 'pytest -v' to see full output."
                )
