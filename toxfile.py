from __future__ import annotations

import typing as t

from tox.plugin import impl

if t.TYPE_CHECKING:
    from tox.tox_env.api import ToxEnv


@impl
def tox_before_run_commands(tox_env: ToxEnv) -> None:
    # determine if it was a parallel invocation by examining the CLI command
    parallel_detected = tox_env.options.command in ("p", "run-parallel")
    if parallel_detected:
        # tox is running parallel, set an indicator env var
        # and effectively disable pytest-xdist by setting xdist-workers to 0
        # -- 0 means tests will run in the main process, not even in a worker
        setenv = tox_env.conf.load("set_env")
        setenv.update({"TOX_PARALLEL": "1", "PYTEST_XDIST_AUTO_NUM_WORKERS": "0"})
