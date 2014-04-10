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


class ActionCardTestMixin(object):

    def assert_action_returned(self, **action_attributes):
        for action in self.action_card:
            if action == action_attributes:
                return
        raise AssertionError(
            'Expected action_attributes {0} to be in {1}'.format(
                action_attributes, self.action_card))
