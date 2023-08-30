from __future__ import annotations

import pathlib
import re


def write_simple_assignment(
    path: str | pathlib.Path, key: str, value: str
) -> str | None:
    if isinstance(path, str):
        path = pathlib.Path(path)

    line_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.*)$")
    with path.open("r") as fp:
        content = fp.readlines()

    old_value = None
    with path.open("w") as fp:
        for line in content:
            if m := line_pattern.match(line):
                old_value = m.group(1)
                if old_value.startswith('"') and old_value.endswith('"'):
                    new_value = f'"{value}"'
                elif old_value.startswith("'") and old_value.endswith("'"):
                    new_value = f"'{value}'"
                else:
                    new_value = value

                fp.write(f"{key} = {new_value}\n")
            else:
                fp.write(line)

    if old_value is None:
        return None
    else:
        return old_value.strip("'\"")
