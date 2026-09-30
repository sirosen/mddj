version := `uvx --from "." mddj read version`

default:
    @just --list

verify:
    nox -t verify -j auto

serve-docs:
    uvx nox -s docs
    python -m http.server 8000 -d docs/.nox/docs/doc_build

build:
    uv build

cog-update:
    uvx --from='cogapp==3.6.0' cog -r docs/cli_usage.rst

publish: build
    uvx flit publish

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
