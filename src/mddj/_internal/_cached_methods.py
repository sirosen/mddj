import typing as t

P = t.ParamSpec("P")
R = t.TypeVar("R")
X = t.TypeVar("X", bound="MethodCacheProvider")


class MethodCacheProvider(t.Protocol):
    _method_cache: dict[t.Any, t.Any]


_SENTINEL = object()


# based on the implementation of functools' _lru_cache_wrapper
def _make_key(
    methodname: str, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
) -> tuple[t.Any, ...]:
    key: tuple[t.Any, ...] = (methodname, _SENTINEL) + args
    if kwargs:
        key += (_SENTINEL,)
        for item in kwargs.items():
            key += item
    return key


def cached_method(
    method: t.Callable[t.Concatenate[X, P], R],
) -> t.Callable[t.Concatenate[X, P], R]:
    """
    Decorate an instance method to give it caching behavior.

    The object being decorated must have a ``_method_cache`` attribute.
    """

    def wrapper(instance: X, /, *args: t.Any, **kwargs: t.Any) -> R:
        cache = instance._method_cache
        key = _make_key(method.__name__, args, kwargs)

        value = cache.get(key, _SENTINEL)
        if value is _SENTINEL:
            value = method(instance, *args, **kwargs)
            cache[key] = value
        return value  # type: ignore[no-any-return]

    return wrapper
