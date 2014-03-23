import mock

from familytree import main
from ..helpers import tornado


class WhenCreatingEvent(tornado.JSONMixin, tornado.TornadoTestCase):

    @classmethod
    def make_application(cls):
        return main.Application()

    @classmethod
    def arrange(cls):
        super(WhenCreatingEvent, cls).arrange()
        cls.event_type = str(mock.sentinel.event_type)

    @classmethod
    def act(cls):
        cls.event = cls.post_json('event', {'type': cls.event_type})

    def should_return_created(self):
        self.assertEqual(self.last_response.code, 201)

    def should_return_self_link(self):
        self.assertIn('self', self.event)

    def should_include_self_link_as_location_header(self):
        self.assertEqual(
            self.last_response.headers['Location'], self.event['self'])


class WhenFetchingCreatedEvent(tornado.JSONMixin, tornado.TornadoTestCase):

    @classmethod
    def make_application(cls):
        return main.Application()

    @classmethod
    def arrange(cls):
        super(WhenFetchingCreatedEvent, cls).arrange()
        cls.post_json('event', {'type': 'some event type'})
        cls.event_link = cls.last_response.headers['Location']

    @classmethod
    def act(cls):
        cls.event = cls.get_json(cls.event_link)

    def should_return_ok(self):
        self.assertEqual(self.last_response.code, 200)

    def should_return_correct_self_link(self):
        self.assertEqual(self.event['self'], self.event_link)

    def should_include_delete_action(self):
        self.assertDictContainsSubset(
            {'method': 'DELETE'}, self.event['actions']['delete-event'])
