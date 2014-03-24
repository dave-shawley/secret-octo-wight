import json

from tornado.web import RequestHandler, HTTPError

from . import http


class BaseHandler(RequestHandler):
    supported_media_types = {
        'application/json',
    }

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self._request_body = None

    def get_url_for(self, handler, *args):
        return self.application.get_url_for(self.request, handler, *args)

    def require_request_body(self):
        if self.request.headers.get('Content-Length', '0') == '0':
            raise HTTPError(http.BAD_REQUEST)
        if not self.request.body:
            raise HTTPError(http.BAD_REQUEST)

    def deserialize_model_instance(self, model_class):
        """Parse the body into an instance of ``model_class``.

        :param class model_class: a *model* class that implements
            the ``from_dictionary`` factory class method.
        :raises HTTPError: if a model instance cannot be decoded

        This method follows the *double-dispatch* pattern to create
        a new instance of ``model_class`` by calling its
        ``from_dictionary`` method with the request body.  If the
        request body cannot be decoded into a dictionary, then the
        appropriate :class:`HTTPError` is raised.

        """
        return model_class.from_dictionary(self.request_body)

    def serialize_model_instance(self, model_instance, *actions, **kwds):
        """Send a *model* instance as the response.

        :param model_instance: instance of a *model* class that
            implements an ``as_dictionary`` method.
        :keyword RequestHandler model_handler: the Tornado handler that
            *owns* the model instance.  If present, this parameter is
            used to create the *self* link.
        :param actions: a list of actions represented as dictionary
            instances.

        The actions available for this model instance are passed as
        dictionary instances in the unnamed arguments list.  Each
        instance is a dictionary containing the following members:

        - name: the well-known action name
        - method: the HTTP method to invoke for the action
        - handler: the :class:`RequestHandler` subclass that implements
            the action
        - args: iterable of positional arguments to pass to
            :meth:`get_url_for`

        """
        model_handler = kwds.get('model_handler')
        model_representation = model_instance.as_dictionary()

        if model_handler is not None:
            url = self.get_url_for(model_handler, model_representation['id'])
            model_representation['self'] = url
            self.set_header('Location', url)

        for action in actions:
            action_card = model_representation.setdefault('actions', {})
            action_card[action['name']] = {
                'method': action['method'],
                'url': self.get_url_for(action['handler'], *action['args']),
            }

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(model_representation))

    @property
    def request_body(self):
        """Parse the request body into a dictionary instance.

        :raises HTTPError: if there is something wrong with the body

        This method will extract the body sent in the request into a
        :class:`dict` instance and return it.  If the body cannot be
        decoded, then a :class:`HTTPError` instance is raised with an
        appropriate *status code* set.

        - 400: if the content cannot be decoded
        - 415: if the content type is unsupported
        - 500: if the no handler is available for the content type

        """
        if self._request_body is None:
            self.require_request_body()
            content_type = self.request.headers.get(
                'Content-Type',
                'application/octet-stream'
            )
            if content_type not in self.supported_media_types:
                raise HTTPError(http.UNSUPPORTED_MEDIA_TYPE)
            if content_type.startswith('application/json'):
                self._request_body = json.loads(self.request.body)
            else:
                raise HTTPError(
                    http.INTERNAL_SERVER_ERROR,
                    reason='Unimplemented Content Type',
                    log_message='{0} is not implemented in {1}.{2}'.format(
                        content_type,
                        self.__class__.__name__,
                        'request_body',
                    ),
                )
        return self._request_body
