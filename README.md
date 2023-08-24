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

#### `mddj read requires-python`

Show the `requires_python` field.

#### `mddj read version`

Show the `version`.

## License

`mddj` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
