from mock import Mock
import fluenttest


class TornadoHandlerTestCase(fluenttest.TestCase):

    @classmethod
    def arrange(cls):
        super(TornadoHandlerTestCase, cls).arrange()
        cls.application = Mock()
        cls.application.ui_methods = {}

        cls.request = Mock()
        cls.request.headers = {}
