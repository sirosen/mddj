# mddj

Your DJ of MetaData.

[![PyPI - Version](https://img.shields.io/pypi/v/mddj.svg)](https://pypi.org/project/mddj)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mddj.svg)](https://pypi.org/project/mddj)

-----

**Table of Contents**

- [Overview](#overview)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [License](#license)

## Overview

A CLI for interacting with your python package metadata.

Supports multiple packaging backends via a uniform interface.

## Installation

```console
pipx install mddj
```

## Quickstart

`mddj` supports usage as a CLI and as library!

Here's how you can instantiate read the project version in Python:

```python
from mddj.api import DJ

dj = DJ()
print(dj.read.version())
```

and, equivalently, via the CLI:

```bash
mddj read version
```

## License

`mddj` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
