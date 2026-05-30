.. _config:

Config
======

Configuration for ``mddj`` can be read from a ``tool.mddj`` table in
``pyproject.toml``. No other configuration files are supported.

Additionally, some values can be loaded via environment variables.

``pyproject.toml``
------------------

``tool.mddj.write_version``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This setting controls how version information is written for
``mddj write version`` (CLI) and ``DJ.write.version()`` (API).

The value must be a colon delimited string with two or three values.
Either ``{mode}:{path}:{key}`` or ``{mode}:{key}``.

The ``{mode}`` must be ``"assign"`` or ``"toml"``.
``"assign"`` looks for the first ``=``-delimited assignment in a file, as might
occur in Python, INI config, or other formats.
``"toml"`` parses the file as TOML and updates a key, which may be nested.

``{path}`` defaults to ``pyproject.toml`` if omitted.

``{key}`` is the name of the attribute used to assign a value.

This defaults to ``toml: project.version``.

For example, the following config can be used to target a ``__version__``
attribute in an ``__init__.py`` file in a src-layout project:

.. code-block:: toml

    [tool.mddj]
    write_version = "assign: src/foopkg/__init__.py: __version__"

Or the ``version`` key in ``setup.cfg``:

.. code-block:: toml

    [tool.mddj]
    write_version = "assign: setup.cfg: version"


``tool.mddj.readthedocs.python_version_path``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This setting controls the lookup path inside of ``.readthedocs.yaml`` or
``.readthedocs.yml`` which will be used for the ReadTheDocs reader to find the
python version.
This should be a path in dotted notation, for example, ``"build.commands"``.

Depending on how the reader is configured (see ``python_version_extraction``
below), the path should be either to the version itself, or to a command  or
commands which can be further parsed.

Defaults to ``"build.tools.python"``.


``tool.mddj.readthedocs.python_version_extraction``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The method which should be used to interpret the ``python_version_path``.

``"verbatim"``, the default, means that the value found at the version path is
the Python version.

``"parse_uv_tool_install"`` means that the path is to a command or list of
commands, and the data should be parsed for an invocation of
``uv tool install ... --python X.Y``.

For example, this can be combined with a parse path as follows:

.. code-block:: toml

    [tool.mddj.readthedocs]
    python_version_path = "build.commands"
    python_version_extraction = "parse_uv_tool_install"


Environment Variables
---------------------

``MDDJ_ISOLATED_BUILDS=0``
    This can be set to disable the (default) behavior using
    isolated build environments when getting package metadata.

    This requires that you have installed all of the build-system requirements in
    to the current environment.

``MDDJ_CAPTURE_BUILD_OUTPUT=0``
    This can be set to disable the (default) behavior of capturing and silencing
    build output when a build backend must be invoked.
