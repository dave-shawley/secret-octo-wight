import uuid

from tornado.web import HTTPError

from . import handlers
from . import http
from . import storage


class Person(object):

    """Information about a single person.

    :keyword str display_name: this person's name to use when
        displaying the person
    :keyword person_id: the unique persistence identifier associated
        with this person

    :raises AssertionError: if neither the `display_name` nor the
        `person_id` are included

    """

    def __init__(self, display_name=None, person_id=None):
        assert display_name or person_id

        super(Person, self).__init__()
        self.display_name = display_name
        self.id = person_id
        self.events = []

    def add_event(self, event):
        """Associate an event with this person.

        :param event: the event that this person was involved in

        """
        self.events.append(event)

    def remove_event(self, event):
        """Remove an event associated with this person.

        :param event: the event that this person was involved in
        :raises ValueError: if `event` is not associated with this person

        """
        self.events.remove(event)

    def as_dictionary(self):
        """Return a dictionary representation.

        The result can be used with :meth:`from_dictionary` to
        recreate this person.  In other words,

        >>> me = Person(display_name='me')
        >>> clone = Person.from_dictionary(me.as_dictionary())
        >>> me.display_name == clone.display_name, me.id == clone.id
        (True, True)

        """
        return {
            'display_name': self.display_name,
            'id': self.id,
            'events': self.events,
        }

    @classmethod
    def from_dictionary(cls, person_data):
        """Create a :class:`Person` instance from a dictionary.

        :param dict person_data:
        :returns: a :class:`Person` instance

        >>> data = {'display_name': 'some name', 'id': '1234', 'events': []}
        >>> person = Person.from_dictionary(data)
        >>> person.as_dictionary() == data
        True

        """
        person = Person(
            person_id=person_data.get('id'),
            display_name=person_data['display_name'],
        )
        for event in person_data.get('events', []):
            person.events.append(event)
        return person


class CreatePersonHandler(handlers.BaseHandler):

    """Root resource that creates a person."""

    def post(self):
        """Create a new person.

        :jsonparameter str display_name: the *title* used to display
            this person
        :requestheader Content-Type: describes the enclosed entity

        This endpoint will create a new person and return its canonical
        representation.  The enclosed entity must follow one of the
        formats described under :ref:`Person Representations
        <person_representation>`.

        :responseheader Location: the canonical location for the new
            person resource
        :status 201: a new resource was created
        :status 400: something is wrong with the included
            representation
        :status 415: the enclosed media-type is not recognized

        """
        try:
            a_person = self.deserialize_model_instance(Person)
            a_person.id = uuid.uuid4().hex
            storage.save_item(a_person, a_person.id)

            self.serialize_model_instance(
                a_person,
                {
                    'name': 'delete-person',
                    'method': 'DELETE',
                    'handler': PersonHandler,
                    'args': (a_person.id,)
                },
                model_handler=PersonHandler,
            )
            self.set_status(http.CREATED)

        except KeyError:
            raise HTTPError(http.BAD_REQUEST)


class PersonHandler(handlers.BaseHandler):

    """Manages a person."""

    def get(self, person_id):
        """Retrieve a Person by unique identifier.

        :param person_id: the unique identifier assigned to a person
        :requestheader Accept: the requested representation type

        :status 200: the response contains a representation of the
            requested person
        :status 404: `person_id` refers to a non-existent person

        """
        try:
            a_person = storage.get_item(Person, person_id)
        except storage.InstanceNotFound:
            raise HTTPError(http.NOT_FOUND)

        self.serialize_model_instance(
            a_person,
            {
                'name': 'delete-person',
                'method': 'DELETE',
                'handler': PersonHandler,
                'args': (a_person.id,)
            },
            model_handler=PersonHandler,
        )
        self.set_status(http.OK)

    def delete(self, person_id):
        """Delete a Person

        :param person_id: the unique identifier assigned to a person

        :status 204: the requested person has been deleted
        :status 404: `person_id` refers to a non-existent person

        """
        try:
            storage.delete_item(Person, person_id)
            self.set_status(http.NO_CONTENT)
        except storage.InstanceNotFound:
            raise HTTPError(http.NOT_FOUND)
