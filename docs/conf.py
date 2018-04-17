# -*- coding: utf-8 -*-

import os
import re
import sys
from os.path import join

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.append(os.path.dirname(__file__))

project = 'snowmicropyn'
copyright = '2018, SLF'

# Load the package's __version__.py to get version string
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, '..', 'snowmicropyn', '__init__.py')) as f:
    VERSION = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

release = VERSION
version = '.'.join(release.split('.')[:2])

source_suffix = '.rst'

master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
