from familytree import main
from ..helpers import tornado


class AcceptanceTestCase(tornado.JSONMixin, tornado.TornadoTestCase):
    """Test case for acceptance tests.

    This class is a basic test case that provides functionality
    useful for writing acceptance tests against the JSON/HTTP API.

    """

    @classmethod
    def make_application(cls):
        return main.Application()

    @classmethod
    def make_person(cls, **body):
        """Create a Person instance

        :param body: values to pass in the JSON document to create
            the new person
        :return: the JSON response

        """
        return cls.post_json('person', body)

    @classmethod
    def make_event(cls, **body):
        """Create a Event instance.

        :param body: values to pass in the JSON document to create
            the new event
        :return: the JSON response

        """
        return cls.post_json('event', body)
