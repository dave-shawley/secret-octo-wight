import uuid

from tornado import web

from . import handlers
from . import person
from . import storage


EVENTS = {}


class Event(object):

    """A Event is an interesting occurrence that involves people.

    .. attribute:: people

       a list of links to :class:`~person.Person` representations

    This class implements the :class:`~storage.ModelInstance` methods
    so `Event` instances can be stored using the :mod:`~.storage` module.

    """

    def __init__(self):
        self.id = uuid.uuid4().hex
        self.people = []

    def as_dictionary(self):
        return {
            'id': self.id,
            'people': self.people,
        }

    @classmethod
    def from_dictionary(cls, data):
        if 'id' in data:
            return EVENTS[data['id']]
        event = Event()
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
        global EVENTS

        event = self.deserialize_model_instance(Event)
        EVENTS[event.id] = event
        for person_url in event.people:
            person_id = person_url.split('/')[-1]
            a_person = storage.get_item(person.Person, person_id)
            a_person.add_event(self.get_url_for(EventHandler, event.id))
            storage.save_item(a_person, person_id)
        self.serialize_model_instance(event, model_handler=EventHandler)
        self.set_status(201)


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
            event = EVENTS[event_id]
        except KeyError:
            raise web.HTTPError(404)

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
        self.set_status(200)

    def delete(self, event_id):
        """Delete a Event by unique identifier.

        :param event_id: the unique identifier assigned to an event

        :status 204: the requested event has been deleted
        :status 404: `event_id` refers to a non-existent event

        """
        del EVENTS[event_id]
        self.set_status(204)
