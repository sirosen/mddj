try:
    import importlib_metadata as metadata
except ImportError:
    import importlib.metadata as metadata


__all__ = ("metadata",)
