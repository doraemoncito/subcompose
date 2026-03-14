# Configuration file for the Sphinx documentation builder.
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from importlib.metadata import metadata as _pkg_metadata, version as _pkg_version
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# -- Project information -------------------------------------------------------
# name, version and author are read from pyproject.toml via importlib.metadata
# so that pyproject.toml is the single source of truth.

_meta = _pkg_metadata("subcompose")
_author_field = _meta.get("Author-email") or ""
# Author-email field format (RFC 5322): "Display Name <email@host>"
_author_name = (
    _author_field.split(" <")[0].strip() if " <" in _author_field else _author_field
)

project = _meta.get("Name") or "subcompose"
release = _pkg_version("subcompose")
author = _author_name
copyright = f"2026, {author}"  # noqa: A001

# -- General configuration -----------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ---------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- autodoc options -----------------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"
