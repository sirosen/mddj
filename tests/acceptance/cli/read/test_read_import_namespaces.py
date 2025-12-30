from textwrap import dedent as d

import pytest


def test_read_import_namespaces_from_pyproject_toml(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"
    toml_text = d(
        """\
        [project]
        name = "mypkg"
        version = "1.2.4"
        import-namespaces = ["mypkg"]
        """
    )
    pyproject.write_text(toml_text, encoding="utf-8")

    with chdir(tmp_path):
        cmd = ["mddj", "read", "import-namespaces"]

        run_line(cmd, search_stdout=r"^mypkg$")


@pytest.mark.skip(reason="hatchling does not yet support Import-Namespaces")
def test_read_import_namespaces_from_hatchling_build(chdir, tmp_path, run_line):
    pyproject = tmp_path / "pyproject.toml"

    pyproject.write_text(
        d(
            """\
            [build-system]
            requires = ["hatchling==1.28.0"]
            build-backend = "hatchling.build"

            [tool.hatch.metadata.hooks.custom]

            [project]
            name = "foopkg"
            version = "1.0.0"
            dynamic = ["import-namespaces"]
            """
        ),
        encoding="utf-8",
    )

    # create a hatch_build which populates import-namespaces based on the package name
    (tmp_path / "hatch_build.py").write_text(
        d(
            """\
            from hatchling.metadata.plugin.interface import MetadataHookInterface


            class APINamespaceMetaDataHook(MetadataHookInterface):
                def update(self, metadata):
                    name = metadata["name"]
                    metadata["import-namespaces"] = [name, f"{name}.api"]
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / "foopkg.py").touch()

    with chdir(tmp_path):
        result = run_line(
            "mddj read import-namespaces", search_stdout=(r"^foopkg$", r"^foopkg.api$")
        )
        assert len(result.stdout.splitlines()) == 2
