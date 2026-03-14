Installation
============

Requirements
------------

* Python 3.14 or later
* Docker with Compose V2 (``docker compose``)
* Poetry (for development)

Install from PyPI
-----------------

.. code-block:: console

   $ pip install subcompose

Install from source
-------------------

Clone the repository and install the package with Poetry:

.. code-block:: console

   $ git clone https://github.com/doraemoncito/subcompose.git
   $ cd subcompose
   $ poetry install

This installs the ``subcompose`` command into the Poetry-managed virtual
environment.  Activate it with:

.. code-block:: console

   $ poetry shell

Or prefix every invocation with ``poetry run``:

.. code-block:: console

   $ poetry run subcompose --help

