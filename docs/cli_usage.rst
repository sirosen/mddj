mddj CLI
========

``mddj`` provides a CLI to help you read, write, and remix your metadata.

Commands
--------

See ``--help`` on each command for more detail on supported options.

``mddj self version``
^^^^^^^^^^^^^^^^^^^^^

Show the version of ``mddj``.

``mddj read requires-python``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Show the ``requires_python`` field.

``mddj read version``
^^^^^^^^^^^^^^^^^^^^^

Show the ``version``.

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
