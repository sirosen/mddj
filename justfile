version := `uvx --from "." mddj read version`

serve-docs:
    uvx --with 'tox-uv' tox r -e docs
    python -m http.server 8000 -d .tox/docs/doc_build

build:
    uv build

cog-update:
    uvx --from='cogapp==3.6.0' cog -r docs/cli_usage.rst

check-sdist:
    uvx --from='check-sdist==1.3.1' check-sdist --inject-junk

publish: build
    uvx flit publish

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
