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

### `mddj read`

Read metadata from your package by building it to an sdist and then inspecting
that `sdist`.

#### `mddj read requires-python`

Show the `Requires-Python` data. Supports specialized options for parsing data
like `--lower-bound`.

See `--help` for details.

## License

`flake8-typing-as-t` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
