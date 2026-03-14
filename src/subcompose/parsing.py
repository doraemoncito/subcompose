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

"""Parsing utilities for subcompose."""

import logging
from typing import Any, Dict, List


def get_groups_from_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Extracts group definitions from the compose data.

    Args:
        data (Dict[str, Any]): The parsed YAML data from the compose file.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are group names and values are lists of service names.
    """
    groups = {}
    try:
        if data and isinstance(data, dict) and "services" in data:
            groups["all"] = sorted(list(data["services"].keys()))
            for service_name, service_config in data["services"].items():
                service_groups = service_config.get("x-subcompose-groups", [])
                if isinstance(service_groups, str):
                    service_groups = [g.strip() for g in service_groups.split(",")]
                for group in service_groups:
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(service_name)

    except Exception as e:
        logging.debug(f"Could not extract groups from data: {e}")
        pass

    return groups
