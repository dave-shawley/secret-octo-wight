from __future__ import print_function, absolute_import

import json
import socket
import sys
import unittest

from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httpserver import HTTPServer
from werkzeug.http import parse_options_header
import fluenttest

from familytree import http


if sys.version_info[0] < 3:
    def is_string(obj):
        return isinstance(obj, basestring)
else:
    def is_string(obj):
        return isinstance(obj, str)


def log(msg_format, *args, **kwargs):  # pragma nocover
    print(msg_format.format(*args, **kwargs), file=sys.stderr)


class TornadoTestCase(fluenttest.TestCase, unittest.TestCase):
    show_trace = False
    last_response = None

    @classmethod
    def make_application(cls):  # pragma nocover
        """Implement this to return the application under test."""

    @classmethod
    def arrange(cls):
        super(TornadoTestCase, cls).arrange()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        for port in range(32000, 32768):
            try:
                sock.setblocking(0)
                sock.bind(('127.0.0.1', port))
                sock.listen(128)
            except IOError:
                pass
        sock_address = sock.getsockname()
        assert sock_address[1] != 0

        cls.my_url = 'http://{0}:{1}'.format(*sock_address)
        cls.last_response = None
        cls.application = cls.make_application()

        cls.io_loop = IOLoop()
        cls.io_loop.make_current()

        cls.client = AsyncHTTPClient(io_loop=cls.io_loop)
        cls.server = HTTPServer(cls.application, io_loop=cls.io_loop)
        cls.server.add_sockets([sock])

    @classmethod
    def teardown_class(cls):
        cls.io_loop.clear_current()
        cls.io_loop.close(all_fds=True)
        super(TornadoTestCase, cls).teardown_class()

    @classmethod
    def _stop(cls, arg=None, **kwargs):
        result = kwargs or arg
        cls.io_loop.stop()
        if cls.show_trace:  # pragma nocover
            if result:
                if hasattr(result, 'request'):
                    log('REQUEST: {0.method} {0.url}', result.request)
                if hasattr(result, 'effective_url'):
                    log('EFFECTIVE URL: {0}', result.effective_url)
                if hasattr(result, 'headers'):
                    for k, v in result.headers.items():
                        log('HEADER: {0}: {1}', k, v)
            else:
                log('stop called without arguments')
        cls._result = result  # curry result for use in _wait

    @classmethod
    def _wait(cls):
        def timeout():  # pragma no cover
            try:
                raise AssertionError('timeout failure')
            finally:
                cls._stop()

        tmo_handle = cls.io_loop.add_timeout(cls.io_loop.time() + 1, timeout)
        cls.io_loop.start()
        cls.io_loop.remove_timeout(tmo_handle)

        cls.last_response = cls._result
        cls._result = None

    @classmethod
    def _fetch(cls, method, request):
        cls.last_response, cls._result = None, None
        if is_string(request):
            request = cls.build_request(request)
        request.method = method
        cls.client.fetch(request, callback=cls._stop)
        cls._wait()
        return cls.last_response

    @classmethod
    def get(cls, request):
        return cls._fetch('GET', request)

    @classmethod
    def post(cls, request):
        return cls._fetch('POST', request)

    @classmethod
    def build_request(cls, path, **kwargs):
        return HTTPRequest(http.urljoin(cls.my_url, path), **kwargs)

    @classmethod
    def header(cls, header_name, default_value=None):
        return cls.last_response.headers.get(header_name, default_value)


class JSONMixin(object):

    @classmethod
    def decode_json_response(cls):
        if not cls.last_response.error:
            content_type = parse_options_header(
                cls.header('Content-Type', 'application/octet-stream'))
            assert content_type[0].startswith('application/json')
            return json.loads(cls.last_response.body)
        return None

    @classmethod
    def build_request(cls, path, **kwargs):
        if 'body' in kwargs:
            kwargs['body'] = json.dumps(kwargs['body'])
        request = super(JSONMixin, cls).build_request(path, **kwargs)
        request.headers['Accept'] = 'application/json'
        return request

    @classmethod
    def get_json(cls, path):
        cls.get(path)
        return cls.decode_json_response()

    @classmethod
    def post_json(cls, path, json_dict):
        request = cls.build_request(
            path,
            body=json_dict,
            headers={'Content-Type': 'application/json'},
        )
        cls.post(request)
        return cls.decode_json_response()
