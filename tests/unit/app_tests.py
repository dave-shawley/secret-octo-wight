import unittest

from mock import Mock, sentinel
import fluenttest

from familytree.main import Application, main
import familytree.person


class WhenApplicationIsCreated(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        cls.tornado_init = cls.patch(
            'familytree.main.tornado.web.Application.__init__',
            return_value=None,
        )

    @classmethod
    def act(cls):
        cls.application = Application()

    @property
    def positional_args(self):
        return self.tornado_init.call_args[0]

    def assert_was_installed(self, handler_class):  # pragma no cover
        for installed in self.positional_args[0]:
            try:
                if installed[1] == handler_class:
                    return
            except TypeError:  # oops... must be a URLSpec
                if installed.handler_class == handler_class:
                    return
        self.fail('expected {0} to be installed'.format(handler_class))

    def should_call_tornado_init(self):
        self.assertEquals(self.tornado_init.call_count, 1)

    def should_install_CreatePersonHandler(self):
        self.assert_was_installed(familytree.person.CreatePersonHandler)

    def should_install_PersonHandler(self):
        self.assert_was_installed(familytree.person.PersonHandler)


class WhenRunningApplication(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        cls.the_application = cls.patch('familytree.main.application')
        cls.IOLoop = cls.patch('familytree.main.tornado.ioloop.IOLoop')

    @classmethod
    def act(cls):
        main()

    @property
    def the_ioloop(self):
        return self.IOLoop.instance.return_value

    def should_tell_application_to_listen(self):
        self.the_application.listen.assert_called_once_with(7654)

    def should_fetch_an_ioloop_instance(self):
        self.IOLoop.instance.assert_called_once_with()

    def should_run_tornado_ioloop(self):
        self.the_ioloop.start.assert_called_once_with()


class _GetUrlForTestCase(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(_GetUrlForTestCase, cls).arrange()

        cls.request = Mock()
        cls.handler_urlspec = Mock()

        cls.application = Application()
        cls.application.named_handlers = Mock()

    @classmethod
    def act(cls):
        cls.result = cls.application.get_url_for(
            cls.request, sentinel.handler)

    def should_lookup_named_handler(self):
        self.application.named_handlers.get.assert_called_once_with(
            sentinel.handler)


class _SuccessfulGetUrlForTestCase(_GetUrlForTestCase):

    @classmethod
    def arrange(cls):
        super(_SuccessfulGetUrlForTestCase, cls).arrange()
        cls.urljoin = cls.patch('familytree.main.http').urljoin

    def should_extract_full_url_from_request(self):
        self.request.full_url.assert_called_once_with()

    def should_reverse_urlspec(self):
        self.handler_urlspec.reverse.assert_called_once_with()

    def should_generate_url_from_urlspec_and_request(self):
        self.urljoin.assert_called_once_with(
            self.request.full_url.return_value,
            self.handler_urlspec.reverse.return_value,
        )

    def should_return_generated_url(self):
        self.assertIs(self.result, self.urljoin.return_value)


class WhenGettingUrlForNamedHandler(_SuccessfulGetUrlForTestCase):

    @classmethod
    def arrange(cls):
        super(WhenGettingUrlForNamedHandler, cls).arrange()
        cls.application.named_handlers.get.return_value = cls.handler_urlspec


class WhenGettingUrlForClass(_SuccessfulGetUrlForTestCase):

    @classmethod
    def arrange(cls):
        super(WhenGettingUrlForClass, cls).arrange()
        cls.handler_urlspec.handler_class = sentinel.handler
        cls.application.named_handlers.get.return_value = None
        cls.application.handlers = [
            (sentinel.host_pattern, [cls.handler_urlspec]),
        ]


class WhenGettingUrlForMissingClass(_GetUrlForTestCase):

    @classmethod
    def arrange(cls):
        super(WhenGettingUrlForMissingClass, cls).arrange()
        cls.application.named_handlers.get.return_value = None
        cls.handler_urlspec.handler_class = sentinel.other_handler
        cls.application.handlers = [
            (sentinel.host_pattern, [cls.handler_urlspec]),
        ]

    def should_return_none(self):
        self.assertIsNone(self.result)
