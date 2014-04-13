"""HTTP helpers

This module is the HTTP abstraction that ``familytree`` uses
instead of ``httplib`` or ``http`` from the standard library.  It
exists to hide some of the Python 2 to Python 3 migration headaches.

"""
try:
    import http.client as _httpclient
except ImportError:  # pragma: no cover
    import httplib as _httpclient

try:
    from urllib.parse import urljoin
except ImportError:  # pragma: no cover
    from urlparse import urljoin


BAD_REQUEST = _httpclient.BAD_REQUEST
CREATED = _httpclient.CREATED
INTERNAL_SERVER_ERROR = _httpclient.INTERNAL_SERVER_ERROR
NOT_FOUND = _httpclient.NOT_FOUND
NO_CONTENT = _httpclient.NO_CONTENT
OK = _httpclient.OK
UNSUPPORTED_MEDIA_TYPE = _httpclient.UNSUPPORTED_MEDIA_TYPE
