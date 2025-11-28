mddj API
========

``mddj``\s API is based around a single object as the point of entry, the
``DJ``, which helps you read, write, and remix your metadata.

Quickstart
----------

Create a DJ and use it to read some metadata:

.. code-block:: python

    from mddj.api import DJ

    dj = DJ()
    print("project version:", dj.read.version())
    print("lowest support Python:", dj.read.requires_python(lower_bound=True))
    print("dependencies:")
    for dep in dj.read.dependencies():
        print("  -", dep)

Or use it to write metadata:

.. code-block:: python

    from mddj.api import DJ

    dj = DJ()
    new_version = "0.99.0"
    old_version = dj.write.version(new_version)
    print(f"updated version from {old_version} to {new_version}")

Caching
-------

Every ``DJ`` instance will aggressively cache loaded TOML data and built
distribution metadata to make operations performant.
If you want to edit metadata and ensure that the caches are cleared, instantiate
a new ``DJ`` object, which will always use its own, fresh cache.

.. note::

    The caching behavior of a ``DJ`` after writes may be improved in the future to
    do more cache invalidations. Currently, the TOML data cache is shared between
    writers and readers, and therefore writes and reads to that data will appear to
    be synchronized within a given ``DJ``.

Configuration
-------------

A ``DJ`` can be configured by means of a ``DJConfig``.
This is the primary interface for programmatically controlling the behavior of
a ``DJ``.

Additionally, configuration will be read from the project's ``pyproject.toml``
file if possible, looking for the ``[tool.mddj]`` table.
See :ref:`the config docs <config>` for details on the TOML configuration.

Reference
---------

.. currentmodule:: mddj.api

.. autoclass:: DJ
    :members:

.. autoclass:: DJConfig
    :members:

Readers
^^^^^^^

.. autoclass:: mddj.api.reader.Reader
    :members:

.. autoclass:: mddj.api.tox_reader.ToxReader
    :members:

.. autoclass:: mddj.api.tox_reader.ToxReaderError
    :members:

Writers
^^^^^^^

.. autoclass:: mddj.api.writer.Writer
    :members:
