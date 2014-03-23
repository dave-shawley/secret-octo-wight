import logging

import helper
import tornado.ioloop
import tornado.log
import tornado.web

from . import __version__
from . import event
from . import http
from . import person


LOGGER = logging.getLogger(__name__)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            ('/event', event.CreateEventHandler),
            ('/event/([a-f0-9]+)', event.EventHandler),
            ('/person', person.CreatePersonHandler),
            ('/person/([a-f0-9]+)', person.PersonHandler),
        ]
        super(Application, self).__init__(handlers)

    def get_url_for(self, request, handler, *args):
        url_spec = self.named_handlers.get(handler)
        if not url_spec:
            for host_patn, specs in self.handlers:
                for cur_spec in specs:
                    if cur_spec.handler_class == handler:
                        url_spec = cur_spec
                        break
        if url_spec is not None:
            return http.urljoin(request.full_url(), url_spec.reverse(*args))
        return None


application = Application()


class Controller(helper.Controller):
    VERSION = __version__

    def __init__(self, *args):
        super(Controller, self).__init__(*args)
        self.io_loop = None

    def run(self):
        """Instantiate and start the IOLoop."""
        LOGGER.info('%s v%s started', self.APPNAME, self.VERSION)
        self.setup()
        self.set_state(self.STATE_ACTIVE)
        application.listen(7654)
        self.io_loop = tornado.ioloop.IOLoop.instance()
        self.io_loop.start()

    def cleanup(self):
        self.io_loop.stop()


def main():
    helper.start(Controller)
