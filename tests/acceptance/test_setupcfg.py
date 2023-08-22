def test_simple_setupcfg_read_python_requires(tmpdir, run_line):
    tmpdir.chdir()
    tmpdir.join("setup.cfg").write(
        """\
[metadata]
name = foopkg
version = 1.0.0

author = Foo
author_email = foo@example.org

[options]
python_requires = >=3.10
"""
    )
    tmpdir.join("setup.py").write("from setuptools import setup; setup()\n")
    tmpdir.join("foopkg.py").write("")

    with tmpdir.as_cwd():
        run_line("mddj read requires-python", search_stdout=r"^>=3\.10$")
