#!/usr/bin/env python3

# Copyright (C) 2026 Jose Hernandez
#
# This file is part of subcompose.
#
# subcompose is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# subcompose is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with subcompose.  If not, see <https://www.gnu.org/licenses/>.

"""
🐳 subcompose: a command line utility to manage subsets of services in Docker compose.yaml files.

Usage:
    subcompose ( -h | --help | -? )
    subcompose ( -v | --version )
    subcompose ( -l | --list ) [--compose-file=<filename>]
    subcompose delete-containers [--debug] [--interpolate] [--all] [--unmanaged] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose delete-images [--debug] [--interpolate] [--unmanaged] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose preview [--debug] [--interpolate] [--unmanaged] [--var-file=<filename>] [--src-tag=<src_tag>] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose pull [--interpolate] [--unmanaged] [--var-file=<filename>] [--src-tag=<src_tag>] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose push [--interpolate] [--unmanaged] [--var-file=<filename>] [--src-tag=<src_tag>] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose run [--debug] [--interpolate] [--unmanaged] [--var-file=<filename>] [--src-tag=<src_tag>] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose stop [--debug] [--interpolate] [--unmanaged] [--service=<service_tag>]... [--group=<group_tag>]... [--compose-file=<filename>]
    subcompose tag [--interpolate] [--unmanaged] [--var-file=<filename>] [--src-tag=<src_tag>] [--service=<service_tag>]... [--group=<group_tag>]... --registry=<registry> --dst-tag=<dst_tag> [--compose-file=<filename>]
    subcompose validate [--debug] [--fix] [--compose-file=<filename>]

Examples:
    subcompose run --group=core
    subcompose run --group=minimal:1.0.0-SNAPSHOT --group=elk:1.0.0-SNAPSHOT --service=elasticsearch:latest --service=kibana:latest
    subcompose run --group=standalone
    subcompose stop --group=standalone
    subcompose --list
    subcompose preview --group=minimal --service=gateway

Please note that it is also possible to launch the docker stack by passing the output of preview to docker compose. e.g.:

    subcompose preview --group=all | docker compose up
    subcompose preview --group=core --group=elk | docker compose up

Options:
    -E --env-var=<variable>       Set ENV variable ( -E AWS_SECRET_ACCESS_KEY=<some_value> -E AWS_DEFAULT_REGION=<some_value> ... )
    -T --dst-tag=<dst_tag>        Set TAG and repo for destination (-T 127.0.0.1:5000:mytag). Uses for tag option only
    -c --compose-file=<filename>  Specify an alternate compose file [default: compose.yaml]
    -d --debug                    Display debug messages in console
    -f --var-file=<filename>      Load variables from file
    -g --group=<group_tag>        Group of services to use (-g group1:tag1 -g group2:tag2 ...)
    -h -? --help                  Show this screen.
    -i --interpolate              Enable variable interpolation
    -l --list                     List of available groups and services
    -r --registry=<registry>      Set registry URL
    -s --service=<service_tag>    Service to use (-s service1:tag1 -s service2:tag2 ...)
    -t --src-tag=<src_tag>        Default image tag
    -u --unmanaged                Exclude managed services
    -v --version                  Show version.

Commands:
    🗑️   delete-containers  Removes specified containers using the auto-generated compose.yaml configuration or all system containers with --all
    🖼️   delete-images      Removes specified images using the auto-generated compose.yaml configuration
    👁️   preview            Prints the auto-generated compose.yaml configuration to the console
    ⬇️   pull               Pulls Docker images to the registry using an auto-generated compose.yaml to obtain image links
    ⬆️   push               Pushes Docker images to the registry using an auto-generated compose.yaml to obtain image links
    🐳   run                Runs the compose project using an auto-generated compose.yaml
    ⏹️   stop               Stops specified containers using the auto-generated compose.yaml configuration
    🏷️   tag                Adds tag to images for services and nested services that are in the script
    🛡️   validate           Validates the groups and dependencies in compose.yaml
"""

import logging
import re
import subprocess
import sys
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Any, Dict

import yaml
from docopt import docopt

from subcompose.constants import (
    ARG_DEBUG,
    ARG_GROUPS,
    ARG_SERVICES,
    ARG_SRC_TAG,
    ARG_UNMANAGED,
    COMPOSE_COMMAND,
)
from subcompose.filtering import (
    filter_by_image_tag,
    remove_dependencies_from_filtered_containers,
)
from subcompose.logger import configure_logging
from subcompose.parsing import get_groups_from_data
from subcompose.substitution import (
    substitute_environment_variables,
    substitute_image_tags,
)
from subcompose.utils import remove_subcompose_keys, represent_none
from subcompose.validation import validate_groups, validate_volumes

BOLD = '\033[1m'
RESET = '\033[0m'

# Function to bold 'subcompose' in any string
def bold_subcompose(text: str) -> str:
    return re.sub(r'(subcompose)', f'{BOLD}\1{RESET}', text, flags=re.IGNORECASE)


def main() -> None:
    # Print banner at the top of every command output
    banner_path = Path(__file__).parent.parent / "banner.txt"
    if banner_path.exists():
        banner = banner_path.read_text()
        print(bold_subcompose(banner))

    try:
        _version = _pkg_version("subcompose")
        arguments: Dict[str, Any] = docopt(__doc__, version=_version)
    except Exception as e:
        print(e)
        sys.exit(1)

    compose_file = "compose.yaml"
    # Pre-scan arguments for compose file to load groups
    # Note: docopt handles arguments, but for dynamic help generation dependent on file content
    # we might need to parse manually or rely on default if available.
    # However, logic in original script was iterating sys.argv manually before docopt.
    # We can keep that logic.
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--compose-file="):
            compose_file = arg.split("=", 1)[1]
        elif (arg == "-c" or arg == "--compose-file") and i + 1 < len(sys.argv):
            compose_file = sys.argv[i + 1]

    content = ""
    data: Dict[str, Any] = {}
    try:
        content = Path(compose_file).read_text()
        data = yaml.safe_load(content) or {}
    except Exception as e:
        logging.debug(f"Could not load groups: {e}")
        pass

    groups = get_groups_from_data(data)

    project_name = data.get("name", "project_name")
    help_groups = f"# {project_name} subcompose groups and services:\n"
    for group_name in sorted(groups.keys()):
        help_groups += f"\n[{group_name}]\n"
        for service in sorted(groups[group_name]):
            help_groups += f"{service}\n"

    if arguments["--list"]:
        print(help_groups)
        return

    debug = arguments[ARG_DEBUG]
    configure_logging(debug)

    logging.debug("Docker subcompose utility started...")

    if arguments[ARG_SERVICES]:
        arguments[ARG_SERVICES] = str(arguments[ARG_SERVICES][0]).split(",")

    logging.debug(f"\nCommand-line arguments:\n{arguments}")

    yaml.add_representer(type(None), represent_none)

    try:
        # If the generated Docker compose file is to be run in interpolation mode then the registry URL is required as
        # part of the image names, allowing the server to know where to pull the images from. Otherwise, if running
        # locally then no registry reference is required as part of the image names.
        if arguments["--interpolate"]:
            content = content.replace("${REGISTRY_URL}/", "")
            data = yaml.safe_load(content) or {}

        project_name = data.get("name", "default")

        required_services = []
        if arguments[ARG_SERVICES]:
            for service in arguments[ARG_SERVICES]:
                service_name = service.split(":")[0]
                if service_name not in groups["all"]:
                    print(
                        f"\nERROR: unknown service '{service_name}' found in command line.\n"
                    )
                    sys.exit(1)
                required_services.append(service_name)

        if arguments[ARG_GROUPS]:
            for group in arguments[ARG_GROUPS]:
                group_name = group.split(":")[0]
                if group_name not in groups:
                    print(f"\nERROR: unknown group '{group}' found in command line.\n")
                    sys.exit(1)
                required_services.extend(groups[group_name])

        # Add dependencies if required
        if arguments["run"] or arguments["preview"]:
            for service in list(required_services):
                if "depends_on" in data["services"][service]:
                    dependencies = data["services"][service]["depends_on"]
                    for dependency in dependencies:
                        if dependency not in groups["all"]:
                            print(
                                f"\nERROR: unknown dependency '{dependency}' listed for service '{service}' in compose.yaml."
                            )
                            sys.exit(1)
                        required_services.append(dependency)

        # Remove duplicates
        required_services = list(set(required_services))

        # Filter out managed services if --unmanaged is specified
        managed_services_set = set()
        if arguments[ARG_UNMANAGED]:
            managed_services_set = {
                s
                for s in required_services
                if data["services"][s].get("x-subcompose-managed", False)
            }
            required_services = [
                s for s in required_services if s not in managed_services_set
            ]

        # Stop or deletes all services if no groups or services specified
        if not required_services and (
            arguments["stop"]
            or arguments["delete-containers"]
            or arguments["delete-images"]
        ):
            for group in groups.values():
                required_services.extend(group)
            required_services = list(set(required_services))

        logging.debug(f"\nRequired services: {sorted(required_services)}")

        # Copy data but replace services with only those required
        required_data = {
            **data,
            "services": {
                s: c
                for s, c in data.get("services", {}).items()
                if s in required_services
            },
            "volumes": data.get("volumes", {}),
        }

        if arguments["validate"]:
            fix = arguments["--fix"]
            issues_groups, fixed_groups = validate_groups(groups, data, fix=fix)
            issues_volumes, fixed_volumes = validate_volumes(data, fix=fix)

            if fix and (fixed_groups or fixed_volumes):
                with open("compose.yaml", "w") as f:
                    yaml.dump(
                        data,
                        f,
                        default_flow_style=False,
                        sort_keys=False,
                        allow_unicode=True,
                    )
                logging.info("Fixed validation warnings and updated compose.yaml.")
            elif not (issues_groups or issues_volumes):
                logging.info("Validation successful. No issues found.")
            return

        # Extract variables to ignore during substitution
        ignored_vars = []
        if not arguments["--interpolate"]:
            # Find all variables in the content to ignore them
            # Matches ${VAR} or $VAR or ${VAR:-default}
            matches = re.findall(
                r"\$\{?([a-zA-Z_][a-zA-Z0-9_]*)(?:[:?].*?)?}?", content
            )
            ignored_vars = list(set(matches))

        # Substitute environment variables
        logging.debug("\nSubstituting environment variables...")
        substituted_data = substitute_environment_variables(
            required_data,
            no_interpolate=not bool(arguments["--interpolate"]),
            ignored_vars=ignored_vars,
        )

        # Identify default image tag
        service_image_tags = {}
        if arguments[ARG_SRC_TAG]:
            service_image_tags = {s: arguments[ARG_SRC_TAG] for s in required_services}

        # Identify group-specific image tags
        if arguments[ARG_GROUPS]:
            for group in arguments[ARG_GROUPS]:
                if ":" in group:
                    group_name, image_tag = group.split(":")
                    for service_name in groups[group_name]:
                        service_image_tags[service_name] = image_tag
                else:
                    for service_name in groups[group]:
                        if service_name not in service_image_tags:
                            service_image_tags[service_name] = None

        # Identify service-specific image tags
        if arguments[ARG_SERVICES]:
            for service in arguments[ARG_SERVICES]:
                if ":" in service:
                    service_name, image_tag = service.split(":")
                    service_image_tags[service_name] = image_tag
                else:
                    if service not in service_image_tags:
                        service_image_tags[service] = None

        # Substitute all image tags
        if service_image_tags:
            logging.debug("Substituting image tags...")
            substituted_data = substitute_image_tags(
                substituted_data, service_image_tags
            )
            # Only stop specified services if they are running
            if (
                arguments["stop"]
                or arguments["delete-containers"]
                or arguments["delete-images"]
            ):
                logging.debug("Filtering running containers by image tags...")
                substituted_data = filter_by_image_tag(
                    substituted_data, service_image_tags
                )

        # Remove dependencies for stopped containers so they can be stopped in isolation from their dependencies.
        if (
            arguments["stop"]
            or arguments["delete-containers"]
            or arguments["delete-images"]
            or arguments[ARG_UNMANAGED]
        ):
            logging.debug("Removing dependencies from filtered containers...")
            substituted_data = remove_dependencies_from_filtered_containers(
                substituted_data,
                groups,
                only_managed=arguments[ARG_UNMANAGED],
                managed_services_set=managed_services_set,
            )

        substituted_data = remove_subcompose_keys(substituted_data)

        effective_docker_compose = yaml.dump(
            substituted_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

        if arguments["preview"] or debug:
            print(bold_subcompose(f"\n{effective_docker_compose}"))
            if arguments["preview"]:
                return

        if arguments["run"]:
            logging.debug(bold_subcompose("\nRunning 'docker compose up' using generated YAML..."))
            cmd_str = f"{COMPOSE_COMMAND} --project-name {project_name} -f - up -d"
            subprocess.run(
                cmd_str,
                input=effective_docker_compose,
                shell=True,
                check=True,
                text=True,
            )
            return

        if arguments["stop"]:
            logging.debug(bold_subcompose("\nRunning 'docker compose stop' using generated YAML..."))
            cmd_str = f"{COMPOSE_COMMAND} --project-name {project_name} -f - stop"
            subprocess.run(
                cmd_str,
                input=effective_docker_compose,
                shell=True,
                check=True,
                text=True,
            )
            return

        if arguments["delete-containers"] or arguments["delete-images"]:
            if arguments["delete-containers"] and arguments["--all"]:
                logging.debug(bold_subcompose("\nDeleting ALL containers on the system..."))
                cmd_str = (
                    "docker stop $(docker ps -a -q) && docker rm -f $(docker ps -a -q)"
                )
                subprocess.run(cmd_str, shell=True, check=False)
                return

            logging.debug(bold_subcompose("\nRunning 'docker compose rm' using generated YAML..."))
            cmd_str = f"{COMPOSE_COMMAND} --project-name {project_name} -f - rm --force --stop"
            subprocess.run(
                cmd_str,
                input=effective_docker_compose,
                shell=True,
                check=True,
                text=True,
            )

            if arguments["delete-images"]:
                logging.debug(bold_subcompose("\nRunning 'docker rmi' against Docker images in generated YAML..."))
                tagged_images = [
                    params["image"]
                    for service, params in substituted_data["services"].items()
                ]
                if tagged_images:
                    cmd_str = f"docker rmi --force {' '.join(tagged_images)}"
                    subprocess.run(cmd_str, shell=True, check=False)
            return

    except yaml.YAMLError as exc:
        print(bold_subcompose(str(exc)))
    except subprocess.CalledProcessError as exc:
        print(bold_subcompose(f"Error running command: {exc}"))
        sys.exit(1)


if __name__ == "__main__":
    main()
