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

"""Filtering logic for subcompose."""

import subprocess
from typing import Any, Dict, List, Optional


def filter_by_image_tag(
    parent: Dict[str, Any], service_image_tags: Dict[str, Optional[str]]
) -> Dict[str, Any]:
    """
    Filters services to only include those that are currently running with the specified image tags.

    Args:
        parent (Dict[str, Any]): The compose data.
        service_image_tags (Dict[str, Optional[str]]): A map of service names to image tags.

    Returns:
        Dict[str, Any]: The filtered compose data.
    """
    # Filter running containers by container name.
    name_filters = '$" -f "name='.join(service_image_tags.keys())
    cmd = f'docker ps -f "name={name_filters}$" --format "{{{{.Names}}}}"'
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, check=False)
    running_containers = result.stdout.decode("utf-8").strip().split("\n")

    parent["services"] = {
        name: params
        for name, params in parent["services"].items()
        if parent["services"][name].get("container_name") in running_containers
        or service_image_tags[name] is None
    }
    return parent


def remove_dependencies_from_filtered_containers(
    parent: Dict[str, Any],
    groups: Dict[str, List[str]],
    only_managed: bool = False,
    managed_services_set: Optional[set[str]] = None,
) -> Dict[str, Any]:
    """
    Removes dependencies from services that are not in the managed groups.

    Args:
        parent (Dict[str, Any]): The compose data.
        groups (Dict[str, List[str]]): The group definitions.
        only_managed (bool): If True, only removes dependencies that are managed externally depending on the deployment.
        managed_services_set (Optional[set[str]]): Set of managed services to remove from dependencies.

    Returns:
        Dict[str, Any]: The updated compose data.
    """
    if managed_services_set is None:
        managed_services_set = {
            s
            for s, c in parent["services"].items()
            if c.get("x-subcompose-managed", False)
        }

    for service_config in parent["services"].values():
        if not only_managed:
            service_config.pop("depends_on", None)
            continue

        depends_on = service_config.get("depends_on")
        if not depends_on:
            continue

        if isinstance(depends_on, list):
            service_config["depends_on"] = [
                s for s in depends_on if s not in managed_services_set
            ]
        elif isinstance(depends_on, dict):
            for s in managed_services_set:
                depends_on.pop(s, None)

        if not service_config["depends_on"]:
            del service_config["depends_on"]

    return parent
