# CHANGELOG

## Unreleased

- Drop support for Python 3.8, Python 3.9
- Update dependency bounds
- Data is now read from `pyproject.toml` when possible, with build metadata
  used as a fallback if that fails

## 0.0.8

- Fix handling of `tox.ini` data to support reading python versions with a dot,
  as in `py3.8,py3.9`

## 0.0.7

- Fix a bug which caused `mddj read tox list-versions` to contain duplicates
  for certain configs

## 0.0.6

- Add `mddj self version` command to see the current `mddj` version

## 0.0.5

- Initial commands in support of reading `tox.ini` data (via subprocess
  invocation of `tox`): `mddj read tox min-version` and
  `mddj read tox list-versions`

## 0.0.4

- Add a command to read `version`: `mddj read version`
- Convert implicit build usage and metadata extraction to use `build.util`
- Support disabling isolated builds via `MDDJ_BUILD_ISOLATION=0` env var
- Add `wheel` as a dependency, and remove `importlib_metadata`
- Add `tomli` as a dependency on pythons below Python 3.11
- Add a command for writing version updates, `mddj write version`
- Config is now supported in the `tool.mddj` table of `pyproject.toml`. Only
  one config value is supported, `write_version`

## 0.0.3

- Support invocation using `python -m`

## 0.0.2

- Fixes to package data

## 0.0.1

- Initial Release
