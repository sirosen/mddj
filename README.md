# mddj

Your DJ of MetaData.

[![PyPI - Version](https://img.shields.io/pypi/v/mddj.svg)](https://pypi.org/project/mddj)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mddj.svg)](https://pypi.org/project/mddj)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Overview

A CLI for interacting with your python package metadata.

Supports multiple packaging backends via a uniform interface.

## Installation

```console
pipx install mddj
```

## Usage

### Env Vars

#### Build Isolation

``MDDJ_ISOLATED_BUILDS=0`` can be set to disable the (default) behavior using
isolated build environments when getting package metadata.

This requires that you have installed all of the build-system requirements in
to the current environment, but will be much faster.

### Commands

See `--help` on each command for more detail on supported options.

#### `mddj self version`

Show the version of `mddj`.

#### `mddj read requires-python`

Show the `requires_python` field.

#### `mddj read version`

Show the `version`.

#### `mddj read tox min-version`

Show the minimum python version in the `tox` env_list.

#### `mddj read tox list-versions`

Show all python versions in the `tox` env_list.

#### `mddj write version`

Write a new version to a target file, defaulting to a `version = ...` assignment
in the `project]` table of `pyproject.toml`.

Supports configuration via `pyproject.toml`.

### Config

Configuration for `mddj` can only be read from a `tool.mddj` table in
`pyproject.toml`. No other configuration sources are supported.

#### `write_version`

This setting controls how version information is written for
`mddj write version`.

It takes a colon delimited string with two or three values.
Either `{mode}:{path}:{key}` or `{mode}:{key}`.

The `{mode}` must be `"assign"` or `"toml"`.
`"assign"` looks for the first `=`-delimited assignment in a file, as might
occur in Python, INI config, or other formats.
`"toml"` parses the file as TOML and updates a key, which may be nested.

`{path}` defaults to `pyproject.toml` if omitted.

`{key}` is the name of the attribute used to assign a value.

This defaults to `toml: project.version`.

For example, the following config can be used to target a `__version__`
attribute in an `__init__.py` file in a src-layout project:

```toml
[tool.mddj]
write_version = "assign: src/foopkg/__init__.py: __version__"
```

Or the `version` key in `setup.cfg`:

```toml
[tool.mddj]
write_version = "assign: setup.cfg: version"
```

## License

`mddj` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
