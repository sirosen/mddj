version := `uvx --from "." mddj read version`

build:
    uv build

check-sdist:
    uvx check-sdist --inject-junk

publish: build
    uvx flit publish

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
