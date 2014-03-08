import json

from tornado.web import HTTPError

from . import handlers
from .http import StatusCodes


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

    def save(self):
        self.id = '1'

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
        }

    @classmethod
    def from_dictionary(cls, person_data):
        """Create a :class:`Person` instance from a dictionary.

        :param dict person_data:
        :returns: a :class:`Person` instance

        >>> data = {'display_name': 'some name', 'id': '1234'}
        >>> person = Person.from_dictionary(data)
        >>> person.as_dictionary() == data
        True

        """
        return Person(
            person_id=person_data.get('id'),
            display_name=person_data['display_name'],
        )


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
            a_person.save()
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
            self.set_status(StatusCodes.CREATED)

        except KeyError:
            raise HTTPError(StatusCodes.BAD_REQUEST)


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
        person = {
            'id': person_id,
            'display_name': 'display name',
        }

        a_person = Person.from_dictionary(person)
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
