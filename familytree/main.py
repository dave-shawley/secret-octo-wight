import urlparse

import tornado.ioloop
import tornado.log
import tornado.web

from .person import CreatePersonHandler, PersonHandler


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            ('/person', CreatePersonHandler),
            ('/person/([0-9]+)', PersonHandler),
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
            return urlparse.urljoin(
                request.full_url(), url_spec.reverse(*args))
        return None


application = Application()


def main():
    application.listen(7654)
    tornado.ioloop.IOLoop.instance().start()
