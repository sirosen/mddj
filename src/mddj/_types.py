from __future__ import annotations

import sys
import typing as t

import tomlkit

if sys.version_info >= (3, 13):
    from typing import TypeIs
else:
    from typing_extensions import TypeIs

TomlValue: t.TypeAlias = tomlkit.items.Item | tomlkit.container.Container
TomlTable: t.TypeAlias = tomlkit.items.Table | tomlkit.items.InlineTable
TomlArray: t.TypeAlias = tomlkit.items.Array | tomlkit.items.AoT
TomlMapping: t.TypeAlias = tomlkit.TOMLDocument | TomlTable


def is_toml_array(obj: t.Any) -> TypeIs[TomlArray]:
    return isinstance(obj, (tomlkit.items.Array, tomlkit.items.AoT))


def is_toml_table(obj: t.Any) -> TypeIs[TomlTable]:
    return isinstance(obj, (tomlkit.items.Table, tomlkit.items.InlineTable))


def is_toml_mapping(obj: t.Any) -> TypeIs[TomlMapping]:
    return isinstance(
        obj, (tomlkit.TOMLDocument, tomlkit.items.Table, tomlkit.items.InlineTable)
    )
