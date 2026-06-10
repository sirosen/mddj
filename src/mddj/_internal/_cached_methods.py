"""
An implementation of method caching as proposed for `functools` itself in
https://github.com/python/cpython/pull/150002
"""

import functools
import typing as t
import weakref

T = t.TypeVar("T")
R = t.TypeVar("R")
P = t.ParamSpec("P")

F = t.TypeVar("F", bound=t.Callable[..., t.Any])


def _cached_method_weakref_callback(
    cache_dict: dict[int, T], id_key: int
) -> t.Callable[[weakref.ref[R]], None]:
    def callback(ref: weakref.ref[R]) -> None:
        cache_dict.pop(id_key)

    return callback


def _wrap_unbound_cached_method(
    ref: weakref.ref[R],
    unbound_method: t.Callable[t.Concatenate[R, P], T],
    maxsize: int | None,
    typed: bool,
) -> t.Callable[P, T]:
    @functools.lru_cache(maxsize, typed)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        self_val: R = ref()  # type: ignore[assignment]
        return unbound_method(self_val, *args, **kwargs)

    return wrapped  # type: ignore[return-value]


class _cached_method:
    """
    A caching decorator for use on instance methods.

    Using cache or lru_cache on methods is problematic because the instance is put into
    the cache and cannot be garbage collected until the cache is cleared. This decorator
    uses a cache based on `id(self)` and a weakref to clear cache entries.

    The instance must be weak-referencable.

    By default, this provides an infinite sized cache similar to functools.cache. Use
    *maxsize* and *typed* to set these attributes of the underlying LRU cache.
    """

    def __init__(
        self,
        func: t.Callable[..., t.Any],
        /,
        maxsize: int | None = None,
        typed: bool = False,
    ) -> None:
        self._function_table: dict[
            int, tuple[weakref.ref[object], t.Callable[..., t.Any]]
        ] = {}

        self._maxsize = maxsize
        self._typed = typed

        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, instance: t.Any, *args: t.Any, **kwargs: t.Any) -> t.Any:
        cached_func = self._get_or_create_cached_func(instance)
        return cached_func(*args, **kwargs)

    def __get__(
        self, instance: t.Any | None, owner: t.Any | None = None
    ) -> t.Callable[..., t.Any]:
        if instance is None:
            return self
        return self._get_or_create_cached_func(instance)

    def _get_or_create_cached_func(self, instance: t.Any) -> t.Callable[..., t.Any]:
        # similar to singledispatch(), defer use of weakref until/unless it
        # is needed
        import weakref

        instance_id = id(instance)

        try:
            ref, cached_func = self._function_table[instance_id]
        except KeyError:
            ref = weakref.ref(
                instance,
                _cached_method_weakref_callback(self._function_table, instance_id),
            )
            cached_func = _wrap_unbound_cached_method(
                ref, self.func, self._maxsize, self._typed
            )
            self._function_table[instance_id] = ref, cached_func

        return cached_func


@t.overload
def cached_method(  # noqa: E704
    func: None = None,
    /,
    maxsize: int | None = None,
    typed: bool = False,
) -> t.Callable[[F], F]: ...


@t.overload
def cached_method(  # noqa: E704
    func: F,
    /,
    maxsize: int | None = None,
    typed: bool = False,
) -> F: ...


def cached_method(
    func: F | None = None, /, maxsize: int | None = None, typed: bool = False
) -> F | t.Callable[[F], F]:
    if func is None:

        def decorator(func: F) -> F:
            return _cached_method(  # type: ignore[return-value]
                func, maxsize=maxsize, typed=typed
            )

        return decorator
    else:
        return _cached_method(func, maxsize=maxsize, typed=typed)
