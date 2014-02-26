# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

import familytree


sys.path.insert(0, os.path.abspath('.'))

needs_sphinx = '1.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinxcontrib.httpdomain',
    'sphinxcontrib.autohttp.tornado',
]
source_suffix = '.rst'
master_doc = 'index'
project = 'Family Tree'
copyright = '2014, Dave Shawley'

# The short X.Y version.
version = familytree.__version__
# The full version, including alpha/beta/rc tags.
release = familytree.__version__

exclude_patterns = []
pygments_style = 'sphinx'

html_theme = 'nature'
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'mock': ('http://mock.readthedocs.org/en/latest/', None),
    'tornado': ('http://www.tornadoweb.org/en/branch3.2/', None),
}

