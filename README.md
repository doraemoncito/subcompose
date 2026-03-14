# 🐳 subcompose

[![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/downloads/release/python-314/) 
[![PyPI Version](https://img.shields.io/pypi/v/subcompose.svg)](https://pypi.org/project/subcompose/) 
[![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/doraemoncito/subcompose/blob/main/LICENSE) 
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://doraemoncito.github.io/subcompose/) 
[![GitHub](https://img.shields.io/badge/source-GitHub-black)](https://github.com/doraemoncito/subcompose) 

A command line utility to manage subsets of services in `compose.yaml` files.

## Features

- Manage and run subsets of services from a Docker Compose file
- Group services for flexible orchestration
- Validate and preview Compose configurations
- Delete containers and images by group
- CLI and Python API usage
- Example Compose file included

## Overview

SubCompose helps you orchestrate, validate, and manage complex Docker Compose setups by grouping services and providing advanced CLI operations.

# Quick Installation

You can install SubCompose directly from the GitHub releases or from PyPI.

## Install from GitHub releases

```bash
pip install https://github.com/doraemoncito/subcompose/archive/refs/tags/vX.Y.Z.tar.gz
```

Replace `vX.Y.Z` with the desired release version.

## Install from PyPI

```bash
pip install subcompose
```

After installation, you can run SubCompose as a command:

```bash
subcompose --help
```

---

> **Developer Instructions:**
> The following section is for contributors and developers who want to install from source or run tests.

## Local Installation from Source

1. Install poetry if you don't have it already. The officially recommended approach is via the installer script which uses Python itself and works on macOS, Linux, and Windows:

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    pipx install poetry
    ```

    This method has several advantages:

    - Isolated install (no dependency conflicts)
    - Uses your system Python
    - Easy upgrades

    Upgrade later with:

    ```bash
    pipx upgrade poetry
    ```

2. Install subcompose using Poetry:

    ```bash
    poetry install
    ```

## Usage

To see available commands:

```bash
subcompose --help
```

## Example Compose File

An example Compose file is provided at `examples/compose.yaml`. You can use this as a template for your own projects.

## License

This project is licensed under the GPL v3. See the [LICENSE](LICENSE) file for details.
