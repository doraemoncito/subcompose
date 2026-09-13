Installation
============

Requirements
------------

* Python 3.10 or later
* Docker with Compose V2 (``docker compose``)
* uv (for development)

Install from PyPI
-----------------

.. code-block:: console

   $ pip install subcompose

Install from source
-------------------

Clone the repository and install the package with `uv <https://docs.astral.sh/uv/>`__:

.. code-block:: console

   $ git clone https://github.com/doraemoncito/subcompose.git
   $ cd subcompose
   $ uv sync

This installs the ``subcompose`` command into the ``.venv`` virtual
environment in the project root.  Activate it with:

.. code-block:: console

   $ source .venv/bin/activate

Or prefix every invocation with ``uv run``:

.. code-block:: console

   $ uv run subcompose --help
