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


"""Constants for subcompose."""

import logging

ARG_SERVICES = "--service"
ARG_GROUPS = "--group"
ARG_SRC_TAG = "--src-tag"
ARG_DEBUG = "--debug"
ARG_COMPOSE_FILE = "--compose-file"
ARG_UNMANAGED = "--unmanaged"

COMPOSE_COMMAND = "docker compose"
MAX_LEVELNAME_LEN = max(
    (len(str(name)) for name in logging.getLevelNamesMapping().keys()), default=0
)
