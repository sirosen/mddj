from __future__ import annotations

import datetime
import typing as t

TomlValue: t.TypeAlias = (
    "dict[str, TomlValue] | list[TomlValue] | str | int | datetime.datetime"
)
