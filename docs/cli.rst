CLI Reference
=============

Synopsis
--------

.. code-block:: text

   subcompose ( -h | --help | -? )

   subcompose ( -v | --version )

   subcompose ( -l | --list )
      [--compose-file=<filename>]

   subcompose delete-containers
      [--debug] [--interpolate] [--all] [--unmanaged]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose delete-images
      [--debug] [--interpolate] [--unmanaged]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose preview
      [--debug] [--interpolate] [--unmanaged]
      [--var-file=<filename>] [--src-tag=<src_tag>]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose pull
      [--interpolate] [--unmanaged]
      [--var-file=<filename>] [--src-tag=<src_tag>]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose push
      [--interpolate] [--unmanaged]
      [--var-file=<filename>] [--src-tag=<src_tag>]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose run
      [--debug] [--interpolate] [--unmanaged]
      [--var-file=<filename>] [--src-tag=<src_tag>]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose stop
      [--debug] [--interpolate] [--unmanaged]
      [--service=<service_tag>]... [--group=<group_tag>]...
      [--compose-file=<filename>]

   subcompose tag
      [--interpolate] [--unmanaged]
      [--var-file=<filename>] [--src-tag=<src_tag>]
      [--service=<service_tag>]... [--group=<group_tag>]...
      --registry=<registry> --dst-tag=<dst_tag>
      [--compose-file=<filename>]

   subcompose validate
      [--debug] [--fix] [--compose-file=<filename>]

Commands
--------

.. option:: delete-containers

   Remove containers for the selected services. This command stops and deletes containers matching the specified services or groups. Use ``--all`` to stop and remove **all** containers on the system, regardless of their management status. Useful for cleaning up your Docker environment or resetting service state. Combine with ``--unmanaged`` to exclude managed containers, or ``--debug`` for verbose output. Example:

   .. code-block:: bash

      subcompose delete-containers --service=api:latest --all

.. option:: delete-images

   Remove Docker images for the selected services. This deletes images from your local Docker registry, freeing disk space and ensuring outdated images are not reused. Use ``--service`` or ``--group`` to target specific images. Combine with ``--unmanaged`` to exclude managed images. Example:

   .. code-block:: bash

      subcompose delete-images --group=core:1.0.0

.. option:: preview

   Print the generated ``compose.yaml`` to standard output. This allows you to review or pipe the output directly into ``docker compose`` for ad-hoc runs. Use ``--var-file`` to inject variables, ``--src-tag`` to set image tags, and ``--interpolate`` for shell-style variable expansion. Example:

   .. code-block:: bash

      subcompose preview --var-file=vars.env | docker compose -f - up

.. option:: pull

   Pull Docker images for the selected services from their registry. Ensures your local environment uses the latest images. Use ``--service`` or ``--group`` to specify targets, ``--src-tag`` to set tags, and ``--var-file`` for variable substitution. Example:

   .. code-block:: bash

      subcompose pull --service=api:latest

.. option:: push

   Push Docker images for the selected services to a registry. Use this to upload built images to a remote registry for sharing or deployment. Specify services/groups, tags, and registry as needed. Example:

   .. code-block:: bash

      subcompose push --group=core --src-tag=1.0.0

.. option:: run

   Start the selected services using ``docker compose up -d``. This launches containers in detached mode. Use ``--debug`` for verbose logs, ``--var-file`` for variable injection, and ``--interpolate`` for variable expansion. Example:

   .. code-block:: bash

      subcompose run --service=api:latest --debug

.. option:: stop

   Stop the selected services using ``docker compose stop``. This halts running containers without removing them. Use ``--service`` or ``--group`` to specify targets, ``--debug`` for verbose output. Example:

   .. code-block:: bash

      subcompose stop --group=core

.. option:: tag

   Re-tag Docker images for the selected services and push them to a registry. Use ``--registry`` to specify the destination registry and ``--dst-tag`` for the new tag. Useful for promoting images between environments or registries. Example:

   .. code-block:: bash

      subcompose tag --service=api:latest --registry=myregistry.com --dst-tag=prod

.. option:: validate

   Validate groups and volume references in the compose file. Checks for configuration errors, missing references, or misconfigurations. Use ``--fix`` to automatically correct detected issues, and ``--debug`` for detailed output. Example:

   .. code-block:: bash

      subcompose validate --fix --debug

Options
-------

.. option:: -c <filename>, --compose-file=<filename>

   Compose file to read.  Defaults to ``compose.yaml``.

.. option:: -d, --debug

   Enable verbose debug output.

.. option:: -E <variable>, --env-var=<variable>

   Set an environment variable used during substitution
   (e.g. ``-E AWS_REGION=eu-west-1``).

.. option:: -f <filename>, --var-file=<filename>

   Load substitution variables from a file.

.. option:: -g <group_tag>, --group=<group_tag>

   Select a named group of services.  Append ``:<tag>`` to pin an image tag
   for every service in the group (e.g. ``--group=core:1.0.0``).

.. option:: -h, -?, --help

   Show the help screen and exit.

.. option:: -i, --interpolate

   Enable shell-style variable interpolation in image names.

.. option:: -l, --list

   List all available groups and services and exit.

.. option:: -r <registry>, --registry=<registry>

   Docker registry URL used by the ``tag`` command.

.. option:: -s <service_tag>, --service=<service_tag>

   Select an individual service.  Append ``:<tag>`` to pin an image tag
   (e.g. ``--service=api:latest``).

.. option:: -t <src_tag>, --src-tag=<src_tag>

   Default image tag applied to all selected services.

.. option:: -T <dst_tag>, --dst-tag=<dst_tag>

   Destination tag used by the ``tag`` command
   (e.g. ``-T 127.0.0.1:5000:mytag``).

.. option:: -u, --unmanaged

   Exclude services marked ``x-subcompose-managed: true`` from the output.

.. option:: -v, --version

   Print the version and exit.

.. option:: --all

   Used with ``delete-containers`` to target all containers on the system.

.. option:: --fix


   Used with ``validate`` to automatically fix detected issues.

Examples
--------

Here are some practical examples of using the subcompose CLI:


.. rubric:: Delete all containers

Run this command:

.. code-block:: bash

   subcompose delete-containers --all

Removes all containers from the system, regardless of their management status.

.. rubric:: Delete images for a group

Run this command:

.. code-block:: bash

   subcompose delete-images --group=core:1.0.0

Removes Docker images for all services in the 'core' group with tag '1.0.0'.

.. rubric:: Preview compose file with variable substitution

Run this command:

.. code-block:: bash

   subcompose preview --var-file=vars.env | docker compose -f - up

Generates a compose file with variables from 'vars.env' and pipes it to Docker Compose.

.. rubric:: Pull latest image for a service

Run this command:

.. code-block:: bash

   subcompose pull --service=api:latest

Pulls the latest image for the 'api' service.

.. rubric:: Tag and push an image to a registry

Run this command:

.. code-block:: bash

   subcompose tag --service=api:latest --registry=myregistry.com --dst-tag=prod

Re-tags the 'api' image as 'prod' and pushes it to 'myregistry.com'.

.. rubric:: Validate and fix compose file

Run this command:

.. code-block:: bash

   subcompose validate --fix --debug

Validates the compose file and automatically fixes detected issues, with verbose output.
