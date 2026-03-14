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


"""Logging configuration for subcompose."""

import logging
import sys

from subcompose.constants import MAX_LEVELNAME_LEN


def configure_logging(debug: bool) -> None:
    """
    Configure logging for the application.

    Args:
        debug (bool): Whether to enable debug logging.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Remove existing handlers to avoid duplication or wrong configuration
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if debug else logging.INFO)
    formatter = logging.Formatter(
        f"[%(levelname)-{MAX_LEVELNAME_LEN}s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
