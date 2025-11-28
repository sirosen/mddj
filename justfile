version := `uvx --from "." mddj read version`

build:
    uvx --from build pyproject-build .

publish: build
    uvx flit publish

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
