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


"""Validation logic for subcompose."""

import logging
import sys
from typing import Any, Dict, List, Optional


def validate_groups(
    groups: Dict[str, List[str]], data: Dict[str, Any], fix: bool = False
) -> tuple[bool, bool]:
    """
    Validates the groups defined in the compose file.

    This function checks for:
    1. Undefined groups used in services.
    2. Defined groups that are empty (no services assigned).
    3. Missing dependencies within groups (services in a group depending on services not in the group).

    Args:
        groups (Dict[str, List[str]]): A dictionary mapping group names to lists of service names.
        data (Dict[str, Any): The parsed YAML data from the compose file.
        fix (bool): Whether to attempt to fix the issues found.

    Returns:
        tuple[bool, bool]: A tuple containing (issues_found, fixed).
    """
    fixed = False
    issues_found = False

    # Ensure definitions structure exists
    defined_groups_dict = data.setdefault("x-subcompose-groups", {})
    defined_groups = set(defined_groups_dict.keys())

    # 1. Check for undefined groups used in services
    for group_name in groups:
        if group_name == "all" or group_name in defined_groups:
            continue

        logging.warning(
            f"Group '{group_name}' is used in services but not defined in x-subcompose-groups."
        )
        issues_found = True
        if fix:
            logging.info(f"Adding group '{group_name}' to x-subcompose-groups.")
            defined_groups_dict[group_name] = {
                "name": group_name.capitalize(),
                "description": f"Group {group_name} automatically added.",
            }
            fixed = True

    # 2. Check for defined groups that are empty/unused
    # We iterate over a copy of keys because we might delete from the dictionary
    for group_name in list(defined_groups):
        if group_name in groups and groups[group_name]:
            continue

        logging.warning(
            f"Group '{group_name}' is defined but empty (no services assigned)."
        )
        issues_found = True
        if fix:
            logging.info(f"Removing group '{group_name}' from x-subcompose-groups.")
            del defined_groups_dict[group_name]
            fixed = True

    # 3. Check for missing dependencies within groups
    for group_name, services in groups.items():
        if group_name == "all" or not services:
            continue

        for service in services:
            service_config = data["services"].get(service, {})
            depends_on = service_config.get("depends_on")

            if not depends_on:
                continue

            dependencies = (
                list(depends_on.keys()) if isinstance(depends_on, dict) else depends_on
            )

            for dependency in dependencies:
                if dependency in services:
                    continue

                logging.warning(
                    f"Service '{service}' in group '{group_name}' depends on '{dependency}' which is not in the group."
                )
                issues_found = True

                if fix:
                    dep_service = data["services"].get(dependency)
                    if dep_service:
                        logging.info(
                            f"Adding dependency '{dependency}' to group '{group_name}'."
                        )
                        dep_groups = dep_service.setdefault("x-subcompose-groups", [])
                        if group_name not in dep_groups:
                            dep_groups.append(group_name)
                            fixed = True
                    else:
                        logging.error(
                            f"Cannot fix: Dependency '{dependency}' not found in services."
                        )

    return issues_found, fixed


def validate_volumes(data: Dict[str, Any], fix: bool = False) -> tuple[bool, bool]:
    """
    Validates that all defined volumes are used by at least one service.

    Args:
        data (Dict[str, Any]): The parsed YAML data from the compose file.
        fix (bool): Whether to attempt to fix the issues found (remove unused volumes).

    Returns:
        tuple[bool, bool]: A tuple containing (issues_found, fixed).
    """
    fixed = False
    issues_found = False
    defined_volumes = set(data.get("volumes", {}).keys())
    used_volumes = set()

    for service in data.get("services", {}).values():
        for volume in service.get("volumes", []):
            source: Optional[str] = None
            if isinstance(volume, str):
                source = volume.split(":")[0]
            elif isinstance(volume, dict):
                source = volume.get("source")

            if source:
                used_volumes.add(source)

    for volume in defined_volumes:
        if volume not in used_volumes:
            logging.warning(
                f"Volume '{volume}' is defined but not used by any service."
            )
            issues_found = True
            if fix:
                logging.info(f"Removing unused volume '{volume}'.")
                del data["volumes"][volume]
                fixed = True
    return issues_found, fixed


def check_service_extension_chain(parent: Dict[str, Any], service_name: str) -> None:
    """
    Checks for circular dependencies in service extensions.

    Args:
        parent (Dict[str, Any]): The compose data.
        service_name (str): The name of the service to check.
    """
    extension_chain = [service_name]
    while True:
        if service_name not in parent["services"]:
            print(
                f"\nERROR: service '{service_name}' not found in the YAML configuration"
            )
            sys.exit(1)

        service_config = parent["services"][service_name]
        if "image" in service_config:
            break

        if "extends" not in service_config:
            print(
                f"\nERROR: service '{service_name}' doesn't have either an 'image' field or a 'extends' field"
            )
            sys.exit(1)

        extends = service_config["extends"]
        if "service" not in extends:
            print(
                f"\nERROR: no 'service' sub-field contained in the 'extends' field for service '{service_name}'"
            )
            sys.exit(1)

        next_service = extends["service"]
        if next_service in extension_chain:
            print(
                "\nERROR: circular dependency detected in 'extends' fields of following services:"
            )
            print(extension_chain[0])
            for i in extension_chain[1:]:
                print(f"-> {i}")
            print(f"-> {next_service}")
            sys.exit(1)

        extension_chain.append(next_service)
        service_name = next_service
