# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import shutil
import subprocess
from pathlib import Path

project = "sec-parser"
copyright = "2023, Alphanome.AI"  # noqa: A001
author = "Alphanome.AI"


def get_git_tag() -> str:
    git_path = shutil.which("git")
    if git_path is None:
        print("git is not installed or not in the system's PATH.")
        return "unknown"

    try:
        return (
            subprocess.check_output([git_path, "describe", "--tags"])  # noqa: S603
            .strip()
            .decode("utf-8")
        )
    except Exception as e:
        print(f"An error occurred while getting the git tag: {e}")
        return "unknown"


release = get_git_tag()


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.duration",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "nbsphinx",
]
autoapi_type = "python"
autoapi_dirs = [f"{Path(__file__).parents[2]}/sec_parser"]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
