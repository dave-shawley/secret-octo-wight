"""HTTP helpers

This module is the HTTP abstraction that ``familytree`` uses
instead of ``httplib`` or ``http`` from the standard library.  It
exists to hide some of the Python 2 to Python 3 migration headaches.

"""
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


__all__ = (
    'urljoin',
)
