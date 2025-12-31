mddj CLI
========

``mddj`` provides a CLI to help you read, write, and remix your metadata.

Commands
--------

See ``--help`` on each command for more detail on supported options.

``mddj self version``
^^^^^^^^^^^^^^^^^^^^^

Show the version of ``mddj``.

.. [[[cog
.. import cog
.. cog.outl()
.. for var in [
..     ("classifiers", "Classifier"),
..     ("dependencies", "Requires-Dist"),
..     ("description", "Summary"),
..     ("import-names", "Import-Name"),
..     ("import-namespaces", "Import-Namespace"),
..     ("keywords",),
..     ("name",),
..     ("optional-dependencies", ("Provides-Extra", "Requires-Dist")),
..     ("requires-python",),
..     ("version",),
.. ]:
..     name = var[0]
..     dist_name = var[1] if len(var) > 1 else name.title()
..     if isinstance(dist_name, str):
..         dist_name = (dist_name,)
..     header = f"``mddj read {name}``"
..     underline = "^" * len(header)
..     cog.outl(header)
..     cog.outl(underline)
..     cog.outl()
..     dist_name = ", ".join(f"``{d}``" for d in dist_name)
..     cog.outl(f"Show the ``{name}`` ({dist_name}) field for the current project.")
..     cog.outl()
..
.. ]]]

``mddj read classifiers``
^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``classifiers`` (``Classifier``) field for the current project.

``mddj read dependencies``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``dependencies`` (``Requires-Dist``) field for the current project.

``mddj read description``
^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``description`` (``Summary``) field for the current project.

``mddj read import-names``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``import-names`` (``Import-Name``) field for the current project.

``mddj read import-namespaces``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``import-namespaces`` (``Import-Namespace``) field for the current project.

``mddj read keywords``
^^^^^^^^^^^^^^^^^^^^^^

Show the ``keywords`` (``Keywords``) field for the current project.

``mddj read name``
^^^^^^^^^^^^^^^^^^

Show the ``name`` (``Name``) field for the current project.

``mddj read optional-dependencies``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``optional-dependencies`` (``Provides-Extra``, ``Requires-Dist``) field for the current project.

``mddj read requires-python``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``requires-python`` (``Requires-Python``) field for the current project.

``mddj read version``
^^^^^^^^^^^^^^^^^^^^^

Show the ``version`` (``Version``) field for the current project.

.. [[[end]]]

``mddj read tox min-version``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the minimum python version in the ``tox`` env_list.

``mddj read tox list-versions``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Show all python versions in the ``tox`` env_list.

``mddj write version``
^^^^^^^^^^^^^^^^^^^^^^

Write a new version to a target file, defaulting to a ``version = ...`` assignment
in the ``[project]`` table of ``pyproject.toml``.

Supports configuration via ``pyproject.toml``.
See :ref:`the config docs <config>` for details.
