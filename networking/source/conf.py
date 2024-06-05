# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import django
sys.path.insert(0, os.path.abspath('../'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'networking.settings'


django.setup()

project = '"Social Networking"'  # noqa  # pylint: disable=invalid-name
copyright = '2024, Parijat'  # noqa  # pylint: disable=redefined-builtin,invalid-name
author = 'Parijat'  # noqa  # pylint: disable=invalid-name

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'  # noqa  # pylint: disable=invalid-name
html_static_path = ['_static']
