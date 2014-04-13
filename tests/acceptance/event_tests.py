from . import AcceptanceTestCase
from ..helpers.compat import mock


class WhenCreatingEvent(AcceptanceTestCase):

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


class WhenFetchingCreatedEvent(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenFetchingCreatedEvent, cls).arrange()
        cls.make_event(type='some event type')
        cls.event_link = cls.last_response.headers['Location']

    @classmethod
    def act(cls):
        cls.event = cls.get_json(cls.event_link)

    def should_return_ok(self):
        self.assertEqual(self.last_response.code, 200)

    def should_return_correct_self_link(self):
        self.assertEqual(self.event['self'], self.event_link)

    def should_include_delete_action(self):
        self.assert_has_action(self.event, 'delete-event')


class WhenDeletingEvent(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenDeletingEvent, cls).arrange()
        cls.make_event(type='some event type')
        cls.event_link = cls.last_response.headers['Location']
        cls.event = cls.get_json(cls.event_link)

    @classmethod
    def act(cls):
        cls.perform_action(cls.event, 'delete-event')

    def should_return_no_content(self):
        self.assertEqual(self.last_response.code, 204)


class WhenFetchingDeletedEvent(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenFetchingDeletedEvent, cls).arrange()
        cls.make_event(type='some event type')
        cls.event_link = cls.header('Location')
        event = cls.get_json(cls.event_link)
        cls.perform_action(event, 'delete-event')

    @classmethod
    def act(cls):
        cls.http_get(cls.event_link)

    def should_return_not_found(self):
        self.assertEqual(self.last_response.code, 404)
