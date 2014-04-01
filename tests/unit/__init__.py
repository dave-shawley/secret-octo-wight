import fluenttest

from ..helpers.compat import mock


class TornadoHandlerTestCase(fluenttest.TestCase):

    @classmethod
    def arrange(cls):
        super(TornadoHandlerTestCase, cls).arrange()
        cls.application = mock.Mock()
        cls.application.ui_methods = {}

        cls.request = mock.Mock()
        cls.request.headers = {}
