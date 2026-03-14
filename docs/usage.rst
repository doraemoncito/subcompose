Usage
=====

Quick start
-----------

List all groups and services defined in the default ``compose.yaml``:

.. code-block:: console

   $ subcompose --list

Run a named group of services:

.. code-block:: console

   $ subcompose run --group=core

Pipe a preview into ``docker compose``:

.. code-block:: console

   $ subcompose preview --group=core | docker compose -f - up

Compose file
------------

``subcompose`` reads a standard Docker ``compose.yaml`` file enriched with two
custom extension fields:

``x-subcompose-groups``
   A YAML mapping that assigns services to named groups.  Each key is a group
   name; the value is a YAML tag referencing a service list alias.

   .. code-block:: yaml

      x-subcompose-groups:
        core: &core
          - database
          - api
        full: &full
          - *core
          - frontend

``x-subcompose-managed``
   A boolean field placed on each service that declares whether the service is
   *managed externally* — that is, expected to be provided by the surrounding
   infrastructure rather than started by subcompose itself.

   .. code-block:: yaml

      services:
        postgresql:
          image: postgres:16
          x-subcompose-managed: true   # provided by the platform

        backend:
          image: myapp/backend:latest
          x-subcompose-managed: false  # always owned by us

   The field has no effect on normal operation.  Its only purpose is to give
   subcompose enough information to safely strip those services — and every
   ``depends_on`` reference to them — when the :option:`--unmanaged` flag is
   passed (see :ref:`excluding-managed`).

.. _excluding-managed:

Excluding managed services (``--unmanaged``)
--------------------------------------------

Why managed services exist
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A typical project uses two categories of service:

**Application services** (``x-subcompose-managed: false``)
   Services your team builds and owns — backends, frontends, workers.
   These run in Docker regardless of the environment.

**Infrastructure services** (``x-subcompose-managed: true``)
   Databases, message brokers, search engines, caches — services whose
   lifecycle is controlled by whoever owns the environment.  On a developer's
   laptop they run in Docker alongside everything else.  In a shared or
   production environment they are provided by the platform (e.g. AWS RDS,
   CloudAMQP, Elasticsearch Service) and are already running before your
   containers start.

The ``x-subcompose-managed`` flag records this distinction so that the same
``compose.yaml`` can serve both situations without duplication.

How it works
~~~~~~~~~~~~

When :option:`--unmanaged` is passed to any subcompose command:

1. Every service whose ``x-subcompose-managed`` is ``true`` is removed from
   the generated compose file.
2. Any ``depends_on`` entry that pointed *to* a removed service is
   automatically deleted from the remaining services.  Entries that point to
   non-managed services are left intact.

Step 2 is essential: Docker Compose would refuse to start a service that
declares a dependency on a service it cannot find.  Subcompose removes only the
managed entries so that the remaining health-check and ordering constraints
continue to work correctly.

Example
~~~~~~~

Given this excerpt of a ``compose.yaml``:

.. code-block:: yaml

   services:
     postgresql:
       image: postgres:16
       x-subcompose-managed: true

     admin:
       image: myapp/admin:latest
       x-subcompose-managed: false

     backend:
       image: myapp/backend:latest
       x-subcompose-managed: false
       depends_on:
         admin:
           condition: service_started
         postgresql:
           condition: service_healthy

Running ``subcompose preview --group=core`` produces a compose file that
includes **all three services** — suitable for local development where you want
a fully self-contained stack:

.. code-block:: yaml

   services:
     postgresql:
       image: postgres:16
     admin:
       image: myapp/admin:latest
     backend:
       image: myapp/backend:latest
       depends_on:
         admin:
           condition: service_started
         postgresql:
           condition: service_healthy

Running ``subcompose preview --group=core --unmanaged`` produces a compose file
that contains only the **application services**, with the managed dependency
reference surgically removed so Docker Compose does not complain:

.. code-block:: yaml

   services:
     admin:
       image: myapp/admin:latest
     backend:
       image: myapp/backend:latest
       depends_on:
         admin:                    # kept — admin is not managed
           condition: service_started
                                   # postgresql entry removed automatically

Notice that ``backend``'s dependency on ``admin`` is preserved — only the
reference to the managed ``postgresql`` service is stripped.

Environment scenarios
~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 45 35
   :header-rows: 1

   * - Environment
     - Command
     - What starts in Docker
   * - Local development
     - ``subcompose run --group=core``
     - All services, including managed ones (databases, brokers, …)
   * - CI / shared infrastructure
     - ``subcompose run --group=core --unmanaged``
     - Application services only; connects to the shared database and
       broker already running in the environment
   * - Production
     - ``subcompose preview --group=core --unmanaged | docker compose -f - up``
     - Application services only; managed services are platform-provided
       (AWS RDS, CloudAMQP, Elastic Cloud, …)

.. tip::

   When deploying to a shared environment, application services connect to
   the managed infrastructure using environment variables
   (``DATABASE_URL``, ``RABBITMQ_SERVER_URL``, etc.).  Subcompose removes
   the managed containers from the compose file but leaves those environment
   variable references untouched, so the application still finds the
   externally-provided services at the correct host and port.

Default value
~~~~~~~~~~~~~

If a service does not declare ``x-subcompose-managed`` at all, subcompose
treats it as **not managed** (equivalent to ``x-subcompose-managed: false``).
The field only needs to be set to ``true`` for infrastructure services that
should be suppressible with :option:`--unmanaged`.

Groups and services
-------------------

Select services by group
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

   $ subcompose run --group=core

Multiple groups and individual services can be combined:

.. code-block:: console

   $ subcompose run --group=core --group=elk --service=kibana

Pinning image tags
~~~~~~~~~~~~~~~~~~

Append a colon-separated tag to any ``--group`` or ``--service`` argument:

.. code-block:: console

   $ subcompose run --group=core:1.2.0 --service=api:latest

Variable interpolation
----------------------

Enable shell-style variable substitution with ``--interpolate``:

.. code-block:: console

   $ subcompose preview --group=core --interpolate

Validation
----------

Check the compose file for group and volume consistency:

.. code-block:: console

   $ subcompose validate

Automatically fix detected issues:

.. code-block:: console

   $ subcompose validate --fix

