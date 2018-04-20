# -*- coding: utf-8 -*-

import os
import re
import sys
import sys
from os.path import join
from unittest.mock import MagicMock


# This mocking stuff is required to get Read the Docs getting building autodocs.
class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()


MOCK_MODULES = ['numpy', 'pandas', 'PyQt5']
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)


extensions = ['sphinx.ext.autodoc', 'sphinx.ext.extlinks']

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.append(join(os.path.dirname(__file__), '..'))

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

github_url = 'https://github.com/slf-dot-ch/snowmicropyn/tree/{}/%s'.format(release)

extlinks = {
    'github_issue': ('https://github.com/slf-dot-ch/snowmicropyn/issues/%s', 'Issue '),
    'github_tree': ('https://github.com/slf-dot-ch/snowmicropyn/tree/v{}/%s'.format(release), ' '),
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_show_sourcelink = False
