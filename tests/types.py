import os
import types
import typing as t


class ChdirContextManagerType(t.Protocol):
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None: ...


class ChdirType(t.Protocol):
    def __call__(self, path: str | os.PathLike[str]) -> ChdirContextManagerType: ...
