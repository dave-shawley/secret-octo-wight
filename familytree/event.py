import uuid

from tornado import web

from . import handlers
from . import http
from . import person
from . import storage


class Event(object):

    """A Event is an interesting occurrence that involves people.

    .. attribute:: people

       a list of links to :class:`~person.Person` representations

    This class implements the :class:`~storage.ModelInstance` methods
    so `Event` instances can be stored using the :mod:`~.storage` module.

    """

    def __init__(self):
        self.id = None
        self.people = []

    def as_dictionary(self):
        return {
            'id': self.id,
            'people': self.people,
        }

    @classmethod
    def from_dictionary(cls, data):
        event = Event()
        event.id = data.get('id')
        event.people.extend(a_person for a_person in data.get('people', []))
        return event


class CreateEventHandler(handlers.BaseHandler):

    """Root resource that creates a new event."""

    def post(self):
        """Create a new event.

        :jsonparameter str type: open-ended, enumerated event type
        :jsonparameter list people: a list of URLs for the person or
            persons associated with the event

        :responseheader Location: the canonical location for the newly
            created event resource
        :status 201: a new event was created
        :status 400: something is wrong with the included
            representation
        :status 415: the enclosed media-type is not recognized

        """
        event = self.deserialize_model_instance(Event)
        event.id = uuid.uuid4().hex
        storage.save_item(event, event.id)

        event_url = self.get_url_for(EventHandler, event.id)
        for person_url in event.people:
            person_id = person_url.split('/')[-1]
            a_person = storage.get_item(person.Person, person_id)
            a_person.add_event(event_url)
            storage.save_item(a_person, a_person.id)
        self.serialize_model_instance(
            event,
            {
                'name': 'delete-event',
                'method': 'DELETE',
                'handler': EventHandler,
                'args': (event.id,)
            },
            model_handler=EventHandler,
        )
        self.set_status(http.CREATED)


class EventHandler(handlers.BaseHandler):

    """Manipulate a specific Event."""

    def get(self, event_id):
        """Retrieve a Event by unique identifier.

        :param event_id: the unique identifier assigned to an event
        :requestheader Accept: the requested representation type

        :status 200: the response contains a representation of the
            requested Event
        :status 404: `event_id` refers to a non-existent event

        """
        try:
            event = storage.get_item(Event, event_id)
        except storage.InstanceNotFound:
            raise web.HTTPError(http.NOT_FOUND)

        self.serialize_model_instance(
            event,
            {
                'name': 'delete-event',
                'method': 'DELETE',
                'handler': EventHandler,
                'args': (event.id,)
            },
            model_handler=EventHandler,
        )
        self.set_status(http.OK)

    def delete(self, event_id):
        """Delete a Event by unique identifier.

        :param event_id: the unique identifier assigned to an event

        :status 204: the requested event has been deleted
        :status 404: `event_id` refers to a non-existent event

        """
        try:
            the_event = storage.get_item(Event, event_id)
            for url in the_event.people:
                path, person_id = url.rsplit('/', 1)
                a_person = storage.get_item(person.Person, person_id)
                a_person.remove_event(self.request.full_url())
                storage.save_item(a_person, a_person.id)
            storage.delete_item(Event, event_id)
            self.set_status(http.NO_CONTENT)
        except storage.InstanceNotFound:
            raise web.HTTPError(http.NOT_FOUND)
