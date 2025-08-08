import typing as t


class ParseError(ValueError):
    pass


def parse_toml_path(path: str) -> list[str | int]:
    return list(_tokenize(path))


def _tokenize(path: str) -> t.Iterator[str | int]:
    for token, is_quoted in _scan(path):
        if is_quoted:
            yield token
        else:
            try:
                yield int(token)
            except ValueError:
                yield token


def _scan(path: str) -> t.Iterator[tuple[str, bool]]:
    if not path:
        return
    if path[0] == ".":
        raise ParseError("Leading '.' separator.")

    charstack = []

    quote: str | None = None
    # None = default state
    # s = skip next
    # e = reading an escaped char
    state: t.Literal["s", "e"] | None = None
    for i, char in enumerate(path):
        if state == "s":
            state = None
            continue

        try:
            peek: str | None = path[i + 1]
        except IndexError:
            peek = None

        if state == "e":
            charstack.append(char)
            state = None
            continue

        if char == "\\":
            state = "e"
            if peek is None:
                raise ParseError("Terminal escape.")
            continue

        if quote:
            if char != quote:
                charstack.append(char)
            else:
                if peek not in (".", None):
                    raise ParseError("Closed quote was not at end of key.")
                yield "".join(charstack), True
                charstack.clear()

                quote = None
                state = None
            continue

        if char == ".":
            if peek is None:
                raise ParseError("Terminal '.' separator.")
            if peek == ".":
                raise ParseError("Double '.' separator.")
            # skip if we haven't accumulated any chars, which can only happen
            # if we just finished a quoted string
            if not charstack:
                continue
            yield "".join(charstack), False
            charstack.clear()
        elif char in ("'", '"'):
            if charstack:
                raise ParseError(
                    "Quote chars within keys must be escaped "
                    "or the entire key must be quoted."
                )
            quote = char
        else:
            charstack.append(char)

    if quote:
        raise ParseError("Unclosed quoted string.")

    if charstack:
        yield "".join(charstack), False
