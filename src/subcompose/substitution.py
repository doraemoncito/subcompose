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

"""Substitution logic for subcompose."""

import logging
import os
import re
import sys
from typing import Any, Dict, List, Optional

from subcompose.validation import check_service_extension_chain

# Get copy of local environment variables for substitutions later on in the process
env = os.environ.copy()


def substitute_environment_variables(
    node: Any,
    no_interpolate: bool = False,
    ignored_vars: Optional[List[str]] = None,
    key_name: str = "root",
    indent: str = "",
) -> Any:
    """
    Recursively substitutes environment variables in the given node (dict, list, or str).

    Args:
        node (Any): The data structure to process.
        no_interpolate (bool): If True, skips interpolation for variables in ignored_vars.
        ignored_vars (Optional[List[str]]): List of variable names to ignore during interpolation.
        key_name (str): The key name of the current node (for logging).
        indent (str): Indentation string for logging.

    Returns:
        Any: The data structure with environment variables substituted.
    """
    if ignored_vars is None:
        ignored_vars = []
    match node:
        case dict():
            new_node = {}
            for key, value in node.items():
                logging.debug(f"{indent} [NODE] --> '{key}'")
                new_node[key] = substitute_environment_variables(
                    value, no_interpolate, ignored_vars, key, indent + "  "
                )
            logging.debug(f"{indent} [NODE]   '{key_name}' done!")
            return new_node
        case list():
            return [
                substitute_environment_variables(
                    item, no_interpolate, ignored_vars, key_name, indent + "  "
                )
                for item in node
            ]
        case str():
            return _substitute_string(node, no_interpolate, ignored_vars)
        case _:
            return node


def _substitute_string(
    value: str, no_interpolate: bool, ignored_vars: List[str]
) -> str:
    if no_interpolate:
        for env_var in ignored_vars:
            value = re.sub(
                rf"\$({{{env_var}(?::-.*)?}})", lambda x: f"%{x.group(1)}", value
            )

    tmp = re.sub(r"(\${([^}:\s]*?)})", lambda x: env.get(x.group(2), x.group(1)), value)
    # The substitution of '\$\$' for '$' is required for output of echoing the effective_docker_compose object
    # to be correctly parsed by the 'docker compose' command. This is due to a combination of the 'echo' command
    # requiring the dollar symbol to be escaped, and the Docker compose specification not interpolating
    # variables beginning with two dollar symbols:
    # https://github.com/compose-spec/compose-spec/blob/master/spec.md#interpolation
    value = re.sub(
        r"(\${(.*?):-(.*?)})", lambda x: env.get(x.group(2), x.group(3)), tmp
    ).replace("$", "$$")

    if no_interpolate:
        # Restore ignored environment variables
        for env_var in ignored_vars:
            value = re.sub(
                rf"%{{({env_var})(?::-.*)?}}", lambda x: f"${{{x.group(1)}}}", value
            )
        value = value.replace("$$", "$")

    return value


def substitute_image_tags(
    parent: Dict[str, Any], service_image_tags: Dict[str, Optional[str]]
) -> Dict[str, Any]:
    """
    Substitutes image tags in the service definitions.

    Args:
        parent (Dict[str, Any]): The compose data.
        service_image_tags (Dict[str, Optional[str]]): A map of service names to image tags.

    Returns:
        Dict[str, Any]: The updated compose data.
    """
    # Substitute specified image tags into image parameters.
    for service_name in parent["services"]:
        if (
            service_name in service_image_tags
            and service_image_tags[service_name] is not None
        ):
            if "extends" in parent["services"][service_name]:
                # Verify no circular dependencies and that 'extends' fields are set correctly
                check_service_extension_chain(parent, service_name)
            else:
                try:
                    parent["services"][service_name]["image"] = re.sub(
                        r"^([^:\s]*?:)(.*)$",
                        rf"\g<1>{service_image_tags[service_name]}",
                        parent["services"][service_name]["image"],
                    )
                except KeyError:
                    print(
                        f"\nERROR: service '{service_name}' must either contain an 'image' field or through a chain of services extends a service that contains an 'image' field.\n"
                    )
                    sys.exit(1)
    return parent
