from textwrap import dedent as d


def test_read_python_requires_with_full_build_output_shows_all_data(
    chdir, tmp_path, run_line, capfd
):
    setupcfg = tmp_path / "setup.cfg"

    setupcfg.write_text(
        d(
            """\
            [metadata]
            name = foopkg
            version = 1.0.0

            author = Foo
            author_email = foo@example.org

            [options]
            python_requires = >=3.10
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text(
        "from setuptools import setup; setup()\n", encoding="utf-8"
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line(
            "mddj read requires-python",
            search_stdout=r"^>=3\.10$",
            env={"MDDJ_CAPTURE_BUILD_OUTPUT": "false"},
        )
        assert len(result.stdout.splitlines()) == 1

    captured = capfd.readouterr()
    assert len(captured.out.splitlines()) > 1
    assert "running dist_info" in captured.out
