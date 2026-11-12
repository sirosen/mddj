import dataclasses


@dataclasses.dataclass(frozen=True)
class LicenseData:
    """
    This datatype defines license information, as encoded in a Python project's
    metadata.

    It can be extracted from static project data or dynamic data. Because the read of
    data combines multiple sources, but none are guaranteed to be present, all
    attributes are optional.
    """

    #: The full text of the license, if provided in metadata sources.
    #: This will not be populated if a file or files are provided in metadata --
    #: only if the raw license text is part of the metadata.
    license_text: str | None
    #: An SPDX license expression for the license(s) declared in metadata.
    license_expression: str | None
    #: Relative paths to the license file or files. These paths are expected to be
    #: relative to the distribution root, where ``pyproject.toml`` is found.
    license_files: tuple[str, ...] | None

    @property
    def is_empty(self) -> bool:
        """True if all attributes are ``None``. False otherwise."""
        return (
            self.license_text is None
            and self.license_expression is None
            and self.license_files is None
        )
