from __future__ import print_function, absolute_import

import json
import socket
import sys
import unittest
import urlparse

from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httpserver import HTTPServer
from werkzeug.http import parse_options_header
import fluenttest


def log(msg_format, *args, **kwargs):  # pragma nocover
    print(msg_format.format(*args, **kwargs), file=sys.stderr)


def decode_json(response):
    if not response.error:
        content_type = parse_options_header(
            response.headers.get('Content-Type', 'application/octet-stream'))
        assert content_type[0] == 'application/json'
        return json.loads(response.body)
    return None


class TornadoTestCase(fluenttest.TestCase, unittest.TestCase):
    show_trace = False

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
        sockaddr = sock.getsockname()
        assert sockaddr[1] != 0

        cls.my_url = 'http://{0}:{1}'.format(*sockaddr)
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
                if hasattr(cls._result, 'effective_url'):
                    log('EFFECTIVE URL: {0}', result.effective_url)
                if hasattr(cls._result, 'headers'):
                    for k, v in result.headers.iteritems():
                        log('HEADER: {0}: {1}', k, v)
            else:
                log('stop called without arguments')
        cls._result = result

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
    def get(cls, request):
        request.method = 'GET'
        cls.client.fetch(request, callback=cls._stop)
        cls._wait()
        return cls.last_response

    @classmethod
    def post(cls, request):
        request.method = 'POST'
        cls.client.fetch(request, callback=cls._stop)
        cls._wait()
        return cls.last_response

    @classmethod
    def build_request(cls, path, **kwargs):
        return HTTPRequest(urlparse.urljoin(cls.my_url, path), **kwargs)


class JSONMixin(object):

    @classmethod
    def build_request(cls, path, **kwargs):
        if 'body' in kwargs:
            kwargs['body'] = json.dumps(kwargs['body'])
        request = super(JSONMixin, cls).build_request(path, **kwargs)
        request.headers['Accept'] = 'application/json'
        return request

    @classmethod
    def get_json(cls, path):
        request = cls.build_request(path)
        response = cls.get(request)
        return decode_json(response)

    @classmethod
    def post_json(cls, path, json_dict):
        request = cls.build_request(
            path,
            body=json_dict,
            headers={'Content-Type': 'application/json'},
        )
        response = cls.post(request)
        return decode_json(response)
