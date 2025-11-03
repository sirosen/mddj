from __future__ import annotations

import pathlib
import re

import tomlkit

from mddj._toml_path import parse_toml_path
from mddj._types import TomlValue, is_toml_array, is_toml_mapping, is_toml_table


def write_simple_assignment(
    path: str | pathlib.Path, key: str, value: str
) -> str | None:
    if isinstance(path, str):
        path = pathlib.Path(path)

    line_pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.*)$")
    with path.open("r", encoding="utf-8") as fp:
        content = fp.readlines()

    old_value = None
    with path.open("w", encoding="utf-8") as fp:
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


def write_toml_value(
    path: str | pathlib.Path,
    target: str,
    value: str,
) -> str | None:
    """
    Write a value to a given target (as a string) in a TOML file.

    The value must be a string and the TOML traversal must satisfy
    """
    if isinstance(path, str):
        path = pathlib.Path(path)

    target_path = parse_toml_path(target)
    if not target_path:
        msg = "Cannot traverse an empty TOML path."
        raise ValueError(msg)

    with path.open("rb") as read_file_descriptor:
        doc = tomlkit.load(read_file_descriptor)

    write_container, key = _traverse_toml_path_to_write_point(doc, target_path)

    if is_toml_mapping(write_container):
        if isinstance(key, str):
            old_value = write_container[key]
        else:
            msg = "TOML traversal found subtable, but final key in path was an int."
            raise ValueError(msg)
    elif is_toml_array(write_container):
        if isinstance(key, int):
            old_value = write_container[key]
        else:
            msg = "TOML traversal found subtable, but final key in path was a string."
            raise ValueError(msg)
    else:
        msg = (
            "Nontrivial TOML write path must terminate in a table or array, "
            "got scalar."
        )
        raise ValueError(msg)

    if old_value.value == value:
        return None
    elif isinstance(old_value, tomlkit.items.String):
        # check string quoting style (tomlkit does not appear to offer a better API
        # for this)
        if isinstance(
            old_value, tomlkit.items.String
        ) and old_value.as_string().startswith("'"):
            write_value = tomlkit.string(value, literal=True)
        else:
            write_value = tomlkit.string(value)

        # mypy flags this, but we've validated the key type against the container type
        # above -- the narrowed type info is simply not retained
        write_container[key] = write_value  # type: ignore[index]
        with path.open("w", encoding="utf-8") as write_file_descriptor:
            tomlkit.dump(doc, write_file_descriptor)
        return old_value.value
    else:
        msg = "TOML path terminated in a non-string value."
        raise ValueError(msg)


def _traverse_toml_path_to_write_point(
    doc: tomlkit.TOMLDocument, path: list[str | int]
) -> tuple[TomlValue, str | int]:
    """
    Traverse a path in a doc terminating in a table or array, returning the final key
    used to write into that subdoc.

    :raises ValueError: if the path does not match the document shape
    """
    if not path:
        msg = "Cannot traverse an empty TOML path."
        raise ValueError(msg)

    first_key, remainder = path[0], path[1:]
    if not isinstance(first_key, str):
        msg = "The first key of a TOML path must be a string."
        raise ValueError(msg)

    if not remainder:
        return (doc, first_key)

    remainder, final_key = remainder[:-1], remainder[-1]

    element: TomlValue = doc[first_key]
    debug_path: list[int | str] = [first_key]
    for key in remainder:
        if not (is_toml_array(element) or is_toml_table(element)):
            msg = f"TOML path attempted to traverse scalar at {debug_path}"
            raise ValueError(msg)

        if isinstance(key, int) and is_toml_array(element):  # slyp: disable=W200
            element = element[key]
        elif isinstance(key, str) and is_toml_table(element):
            element = element[key]
        else:
            msg = (
                "Error traversing TOML document. "
                f"Encountered improper type at {debug_path}"
            )
            raise ValueError(msg)
        debug_path.append(key)

    return element, final_key
