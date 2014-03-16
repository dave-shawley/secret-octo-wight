"""HTTP helpers

This module is the HTTP abstraction that ``familytree`` uses
instead of ``httplib`` or ``http`` from the standard library.  It
exists to hide some of the Python 2 to Python 3 migration headaches.

"""
try:
    import http.client as _httpclient
except ImportError:
    import httplib as _httpclient

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin


__all__ = (
    'StatusCodes',
    urljoin.__name__,  # avoids flake8 warning
)


class StatusCodes:

    """Central list of HTTP status codes.

    Python 3 moved HTTP status codes from attributes of the ``httplib``
    module to attributes of the ``http.client`` module.  Instead of
    including import magic throughout my code to rectify the difference
    or including yet another 3rd party shim (e.g., ``six``), I'm going
    to place status codes as a attributes on this class.

    """

    BAD_REQUEST = _httpclient.BAD_REQUEST
    CREATED = _httpclient.CREATED
    INTERNAL_SERVER_ERROR = _httpclient.INTERNAL_SERVER_ERROR
    UNSUPPORTED_MEDIA_TYPE = _httpclient.UNSUPPORTED_MEDIA_TYPE
