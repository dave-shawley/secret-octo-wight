import unittest

import fluenttest
import mock

import familytree.main


class ControllerTestCase(fluenttest.TestCase):

    @classmethod
    def arrange(cls):
        cls.controller_init = cls.patch(
            'familytree.main.helper.Controller.__init__', return_value=None)


###############################################################################
### Controller Class
###############################################################################

class TheControllerClass(unittest.TestCase):

    controller = fluenttest.ClassTester(familytree.main.Controller)

    def should_extend_helper_controller(self):
        self.assertTrue(self.controller.is_subclass_of('helper.Controller'))

    def should_define_version_correctly(self):
        self.assertEquals(self.controller.cls.VERSION, familytree.__version__)


###############################################################################
### Controller.__init__
###############################################################################

class WhenCreatingController(ControllerTestCase, unittest.TestCase):

    @classmethod
    def act(cls):
        cls.controller = familytree.main.Controller(
            mock.sentinel.args, mock.sentinel.operating_system)

    def should_call_super_init(self):
        self.controller_init.assert_called_once_with(
            mock.sentinel.args, mock.sentinel.operating_system)

    def should_initialize_io_loop_property(self):
        self.assertIsNone(self.controller.io_loop)


###############################################################################
### Controller.run
###############################################################################

class WhenControllerRuns(ControllerTestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenControllerRuns, cls).arrange()
        cls.application = cls.patch('familytree.main.application')
        tornado_ioloop = cls.patch('familytree.main.tornado.ioloop')
        cls.ioloop_instance = tornado_ioloop.IOLoop.instance
        cls.logger = cls.patch('familytree.main.LOGGER')

        cls.controller = familytree.main.Controller(
            mock.sentinel.args, mock.sentinel.operating_system)
        cls.controller.setup = mock.Mock()
        cls.controller.set_state = mock.Mock()

    @classmethod
    def act(cls):
        cls.controller.run()

    def should_log_that_application_started(self):
        self.logger.info.assert_any_call(
            '%s v%s started',
            self.controller.APPNAME,
            self.controller.VERSION,
        )

    def should_setup_controller(self):
        self.controller.setup.assert_called_once_with()

    def should_set_state_to_active(self):
        self.controller.set_state.assert_called_once_with(
            self.controller.STATE_ACTIVE)

    def should_tell_application_to_listen(self):
        self.application.listen.assert_called_once_with(7654)

    def should_get_ioloop_instance(self):
        self.ioloop_instance.assert_called_once_with()

    def should_start_tornado_ioloop(self):
        self.ioloop_instance.return_value.start.assert_called_once_with()

    def should_save_ioloop_instance(self):
        self.assertIs(
            self.controller.io_loop, self.ioloop_instance.return_value)


###############################################################################
### Controller.cleanup
###############################################################################

class WhenCleaningUpController(ControllerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenCleaningUpController, cls).arrange()
        cls.controller = familytree.main.Controller(
            mock.sentinel.args, mock.sentinel.operating_system)
        cls.controller.io_loop = mock.Mock()

    @classmethod
    def act(cls):
        cls.controller.cleanup()

    def should_stop_io_loop(self):
        self.controller.io_loop.stop.assert_called_once_with()
