# /// script
# dependencies = ["nox", "mddj"]
# ///
import pathlib
import shutil
import sys

import nox

import mddj.api

dj = mddj.api.DJ()
nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "uv|virtualenv"

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHONS = nox.project.python_versions(PYPROJECT)
MAX_PYTHON = max(PYTHONS)  # lexical sort applied via 'max' works
MIN_PYTHON = min(PYTHONS)
RTD_PYTHON = dj.read.readthedocs.python_version()


def _is_parallel(session: nox.Session) -> bool:
    # in future versions of nox, use `session.parallel`
    return "--parallel" in sys.argv


@nox.session(python=MAX_PYTHON, default=False, tags=["lint", "verify"])
def prek(session: nox.Session) -> None:
    """Run linters and fixers."""
    session.install("prek")
    session.run("prek", "run", "--all-files", *session.posargs)


@nox.session(
    python=(MAX_PYTHON, MIN_PYTHON), default=False, tags=["lint", "verify", "typing"]
)
def mypy(session: nox.Session) -> None:
    """Run mypy for type checking."""
    session.install("mypy", *nox.project.dependency_groups(PYPROJECT, "test"))
    session.install("-e.")
    session.run("mypy", "src/", "tests/", *session.posargs)


@nox.session(default=False, tags=["lint", "verify"])
def checkdists(session: nox.Session) -> None:
    """Check distribution data."""
    session.install("check-sdist")
    session.run("check-sdist", "--inject-junk", *session.posargs)


@nox.session(default=False, tags=["lint", "verify"], name="lint-imports")
def lint_imports(session: nox.Session) -> None:
    """Run import linters."""
    session.install("import-linter")
    session.install("-e.")
    session.run("lint-imports", *session.posargs)


@nox.session(
    python=PYTHONS, requires=["covclean"], allow_parallel=True, tags=["verify"]
)
@nox.parametrize("add_dependency_groups", [(), ("tox4",)], ids=["base", "tox"])
def test(session: nox.Session, add_dependency_groups: tuple[str, ...]) -> None:
    """Run tests."""
    session.install(
        *nox.project.dependency_groups(PYPROJECT, "test"),
        *(
            dep
            for group in add_dependency_groups
            for dep in nox.project.dependency_groups(PYPROJECT, group)
        ),
    )
    session.install("-e.")
    env = {"COVERAGE_FILE": str(pathlib.Path.cwd() / f".coverage.{session.python}")}
    if _is_parallel(session):
        env.update({"PYTEST_XDIST_AUTO_NUM_WORKERS": "0"})
    session.run("coverage", "run", "-m", "pytest", "-v", *session.posargs, env=env)


@nox.session(python=MAX_PYTHON)
def covclean(session: nox.Session) -> None:
    """Clean up coverage data."""
    session.install("coverage")
    session.run("coverage", "erase", *session.posargs)


@nox.session(python=MAX_PYTHON, requires=["test"])
def covcombine(session: nox.Session) -> None:
    """Combine coverage data."""
    session.install("coverage")
    session.run("coverage", "combine", *session.posargs)


@nox.session(python=MAX_PYTHON, requires=["covcombine"], tags=["verify"])
def covreport(session: nox.Session) -> None:
    """Create coverage HTML and text reports."""
    session.install("coverage")
    session.run("coverage", "html", "--fail-under=0", *session.posargs)
    session.run("coverage", "report", *session.posargs)


@nox.session(python=MAX_PYTHON, default=False)
def build(session: nox.Session) -> None:
    """Build dists."""
    session.install("build")
    session.run("python", "-m", "build", *session.posargs)


@nox.session(python=RTD_PYTHON, tags=["verify"])
def docs(session: nox.Session) -> None:
    """Build docs."""
    session.install(*nox.project.dependency_groups(PYPROJECT, "docs"))
    session.install("-e.")
    with session.chdir("docs/"):
        tmpdir = session.create_tmp()
        parallel_args = [] if _is_parallel(session) else ["-j", "auto"]
        dest = str(session.env_dir / "doc_build")
        shutil.rmtree(dest, ignore_errors=True)

        session.run(
            "sphinx-build",
            *parallel_args,
            "-d",
            f"{tmpdir}/.doctrees",
            "-b",
            "html",
            "-W",
            ".",
            dest,
        )
