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


"""Utility functions for subcompose."""

from typing import Any


def represent_none(self: Any, _: Any) -> Any:
    """Custom representer for None."""
    return self.represent_scalar("tag:yaml.org,2002:null", "")


def remove_subcompose_keys(data: Any) -> Any:
    """
    Recursively removes keys starting with 'x-subcompose-' from the data.

    Args:
        data (Any): The data structure to clean.

    Returns:
        Any: The cleaned data structure.
    """
    if isinstance(data, dict):
        return {
            k: remove_subcompose_keys(v)
            for k, v in data.items()
            if not k.startswith("x-subcompose-")
        }
    elif isinstance(data, list):
        return [remove_subcompose_keys(item) for item in data]
    else:
        return data
