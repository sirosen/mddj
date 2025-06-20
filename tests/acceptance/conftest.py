import re
import shlex
import textwrap

import pytest
from click.testing import CliRunner

_PYTEST_VERBOSE = False


def pytest_configure(config):
    if config.getoption("verbose") > 0:
        global _PYTEST_VERBOSE
        _PYTEST_VERBOSE = True


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def run_line(cli_runner):
    def func(
        line,
        assert_exit_code=0,
        stdin=None,
        search_stdout=None,
        search_stderr=None,
    ):
        from mddj import main

        # split line into args and confirm line starts with "mddj"
        args = shlex.split(line) if isinstance(line, str) else line
        assert args[0] == "mddj"

        # run the line. main is the "mddj" part of the line
        # if we are expecting success (0), don't catch any exceptions.
        result = cli_runner.invoke(
            main, args[1:], input=stdin, catch_exceptions=bool(assert_exit_code)
        )
        if result.exit_code != assert_exit_code:
            message = f"""\
CliTest run_line exit_code assertion failed!
Line:
  {line}
exited with {result.exit_code} when expecting {assert_exit_code}
"""
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

    return func


def _assert_matches(text, text_name, search):
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
