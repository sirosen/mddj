from __future__ import annotations

from .._internal import _writers
from .config import WriterConfig, WriteVersionAssignSettings, WriteVersionTomlSettings


class Writer:
    """
    A Writer is an interface for data writing capabilities.

    Typically, users should simply create a DJ and then access the writer built by it,
    as in:

    .. code-block:: pycon

        >>> from mddj.api import DJ
        >>> dj = DJ()
        >>> dj.write.version("0.2.0")
        '0.1.0'
    """

    def __init__(self, config: WriterConfig) -> None:
        self.config = config

    def version(self, new_version: str) -> str:
        """
        Write a new version into the project metadata, returning the old version.

        If no previous version can be found, a LookupError is raised, on the presumption
        that this means that the writer is not correctly configured for the project.
        """
        write_version_settings = self.config.write_version_settings

        if isinstance(write_version_settings, WriteVersionAssignSettings):
            result = _writers.write_simple_assignment(
                write_version_settings.file_path,
                write_version_settings.key,
                new_version,
            )
        elif isinstance(write_version_settings, WriteVersionTomlSettings):
            return _writers.write_toml_value(
                write_version_settings.file_path,
                write_version_settings.toml_path,
                new_version,
            )
        else:
            raise NotImplementedError(
                "Unrecognized write_version_config. "
                f"write_version={self.config.write_version}"
            )

        if result is None:
            raise LookupError(
                "No previous version was found, so no update was written."
            )

        return result
