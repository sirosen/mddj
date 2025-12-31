from textwrap import dedent as d


def test_read_static_optional_deps(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.optional-dependencies]
            foo = ["bar<2"]
            baz = ["bar>3", "quux > 4.8"]
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read optional-dependencies")
        assert result.stdout == d(
            """\
            foo:
                bar<2
            baz:
                bar>3
                quux > 4.8
            """
        )


def test_read_static_optional_deps_non_normalized(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.optional-dependencies]
            foo_bar = ["baz"]  # not normalized!
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read optional-dependencies")
        # printed out normalized
        assert result.stdout == d(
            """\
            foo-bar:
                baz
            """
        )

    with chdir(tmp_path):
        # selected non-normalized (will normalize)
        result = run_line("mddj read optional-dependencies --extra foo.bar")
        assert result.stdout == "baz\n"


def test_read_static_optional_deps_select_one(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.optional-dependencies]
            foo = ["bar<2", "snork"]
            baz = ["bar>3", "quux > 4.8"]
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line("mddj read optional-dependencies --extra foo")
        assert result.stdout == d(
            """\
            bar<2
            snork
            """
        )


def test_read_static_optional_deps_select_one_does_not_exist(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["setuptools"]
            build-backend = "setuptools.build_meta"

            [project]
            name = "foopkg"
            version = "1.0.0"

            [project.optional-dependencies]
            foo = ["bar<2", "snork"]
            a_real_empty_extra = []
            """
        ),
        encoding="utf-8",
    )

    with chdir(tmp_path):
        result = run_line(
            "mddj read optional-dependencies --extra bar", assert_exit_code=1
        )
        assert result.stdout == ""
        assert "'bar' does not appear in project extras." in result.stderr
        # the extra names (normalized!) shall appear
        assert "foo" in result.stderr
        assert "a-real-empty-extra" in result.stderr


def test_read_dynamic_optional_deps_strip_extras(chdir, tmp_path, run_line):
    """
    Prove it works by "sufficiently intimidating example"
    """
    setuppy = tmp_path / "setup.py"

    setuppy.write_text(
        d(
            """\
            from setuptools import setup


            setup(
                name="foopkg",
                version="1.0",
                install_requires=[
                    "requests > 2",
                    "rich; extra == 'cli'",
                ],
                extras_require={
                    "cli": [
                        (
                            "colorama; "
                            'platform_system == "Windows" or '
                            'implementation_name != "cpython"'
                        ),
                        "better_tracebacks; extra == 'cli'",
                        "better_tracebacks",
                    ],
                    "better_tb": ["better_tracebacks"],
                },
            )
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read optional-dependencies")

    # setuptools seems to preserve definition order for extras
    # and the sneaky thing added via an extra marker comes first
    # the ordering is not be guaranteed to be stable over time, but it keeps the test
    # simpler to assume it this way for now
    assert result.stdout == d(
        """\
        cli:
            rich
            colorama; platform_system == "Windows" or implementation_name != "cpython"
            better_tracebacks; extra == "cli"
            better_tracebacks
        better-tb:
            better_tracebacks
        """
    )


def test_read_dynamic_optional_deps_exact(chdir, tmp_path, run_line):
    setuppy = tmp_path / "setup.py"

    setuppy.write_text(
        d(
            """\
            from setuptools import setup


            setup(
                name="foopkg",
                version="1.0",
                install_requires=[
                    "requests > 2",
                    "rich; extra == 'cli'",
                ],
                extras_require={
                    "cli": [
                        (
                            "colorama; "
                            'platform_system == "Windows" or '
                            'implementation_name != "cpython"'
                        ),
                        "better_tracebacks; extra == 'cli'",
                        "better_tracebacks",
                    ],
                    "better_tb": ["better_tracebacks"],
                },
            )
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line("mddj read optional-dependencies --exact-wheel-metadata")

    # WARNING: this output is highly dependent on exact setuptools behavior
    assert result.stdout == d(
        """\
        cli:
            rich; extra == "cli"
            colorama; (platform_system == "Windows" or implementation_name != "cpython") and extra == "cli"
            better_tracebacks; extra == "cli" and extra == "cli"
            better_tracebacks; extra == "cli"
        better-tb:
            better_tracebacks; extra == "better-tb"
        """  # noqa: E501
    )
