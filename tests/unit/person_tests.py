import unittest

from mock import Mock, sentinel
from tornado import web
import fluenttest

from familytree import storage
from familytree.person import (
    CreatePersonHandler,
    Person,
    PersonHandler,
)
from . import TornadoHandlerTestCase


###############################################################################
### CreatePersonHandler.post
###############################################################################

class WhenPostingToCreatePersonHandler(TornadoHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenPostingToCreatePersonHandler, cls).arrange()
        cls.storage = cls.patch('familytree.person.storage')
        cls.uuid_module = cls.patch('familytree.person.uuid')
        cls.handler = CreatePersonHandler(cls.application, cls.request)
        cls.handler.deserialize_model_instance = Mock()
        cls.handler.serialize_model_instance = Mock()
        cls.handler.set_status = Mock()

        cls.person = cls.handler.deserialize_model_instance.return_value

    @classmethod
    def act(cls):
        cls.response = cls.handler.post()

    def should_deserialize_model_instance(self):
        self.handler.deserialize_model_instance.assert_called_once_with(
            Person)

    def should_generate_person_id(self):
        self.uuid_module.uuid4.assert_called_once_with()

    def should_save_model_instance(self):
        self.storage.save_item.assert_called_once_with(
            self.handler.deserialize_model_instance.return_value,
            self.uuid_module.uuid4.return_value.hex,
        )

    def should_serialize_model_instance(self):
        self.handler.serialize_model_instance.assert_called_once_with(
            self.person,
            {
                'name': 'delete-person',
                'method': 'DELETE',
                'handler': PersonHandler,
                'args': (
                    self.person.id,
                )
            },
            model_handler=PersonHandler,
        )

    def should_set_status_to_created(self):
        self.handler.set_status.assert_called_once_with(201)


###############################################################################
### PersonHandler.get()
###############################################################################

class _PersonHandlerGetTestCase(TornadoHandlerTestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(_PersonHandlerGetTestCase, cls).arrange()
        cls.get_item = cls.patch('familytree.person.storage.get_item')
        cls.handler = PersonHandler(cls.application, cls.request)

    @classmethod
    def act(cls):
        cls.response = cls.handler.get(sentinel.person_id)

    def should_retrieve_person_from_data_store(self):
        self.get_item.assert_called_once_with(Person, sentinel.person_id)


class WhenPersonHandlerGets(_PersonHandlerGetTestCase):

    @classmethod
    def arrange(cls):
        super(WhenPersonHandlerGets, cls).arrange()
        cls.person = cls.get_item.return_value
        cls.handler.serialize_model_instance = Mock()
        cls.handler.set_status = Mock()

    def should_serialize_model_instance(self):
        self.handler.serialize_model_instance.assert_called_once_with(
            self.person,
            {
                'name': 'delete-person',
                'method': 'DELETE',
                'handler': PersonHandler,
                'args': (
                    self.person.id,
                )
            },
            model_handler=PersonHandler,
        )

    def should_set_status_to_ok(self):
        self.handler.set_status.assert_called_once_with(200)


class WhenPersonHandlerGetsNonexistentPerson(_PersonHandlerGetTestCase):

    allowed_exceptions = web.HTTPError

    @classmethod
    def arrange(cls):
        super(WhenPersonHandlerGetsNonexistentPerson, cls).arrange()
        cls.get_item.side_effect = storage.InstanceNotFound(Mock(), '')

    def should_raise_not_found(self):
        self.assertEqual(self.exception.status_code, 404)


###############################################################################
### PersonHandler.delete
###############################################################################

class _PersonHandlerDeleteTestCase(TornadoHandlerTestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(_PersonHandlerDeleteTestCase, cls).arrange()
        cls.delete_item = cls.patch('familytree.person.storage.delete_item')
        cls.handler = PersonHandler(cls.application, cls.request)

    @classmethod
    def act(cls):
        cls.handler.delete(sentinel.person_id)

    def should_call_delete_item(self):
        self.delete_item.assert_called_once_with(Person, sentinel.person_id)


class WhenPersonHandlerDeletes(_PersonHandlerDeleteTestCase):

    @classmethod
    def arrange(cls):
        super(WhenPersonHandlerDeletes, cls).arrange()
        cls.handler.set_status = Mock()

    def should_set_status_to_no_content(self):
        self.handler.set_status.assert_called_once_with(204)


class WhenPersonHandlerDeletesNonexistentPerson(_PersonHandlerDeleteTestCase):

    allowed_exceptions = web.HTTPError

    @classmethod
    def arrange(cls):
        super(WhenPersonHandlerDeletesNonexistentPerson, cls).arrange()
        cls.delete_item.side_effect = storage.InstanceNotFound(Mock(), '')

    def should_raise_not_found(self):
        self.assertEqual(self.exception.status_code, 404)


###############################################################################
### Person.__init__
###############################################################################

class WhenInitializingPerson(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenInitializingPerson, cls).arrange()
        cls.kwargs = {
            'display_name': sentinel.display_name,
            'person_id': sentinel.person_id,
        }

    @classmethod
    def act(cls):
        cls.person = Person(**cls.kwargs)

    def should_not_have_events(self):
        self.assertEqual(len(self.person.events), 0)


class WhenInitializingPersonWithoutDisplayNameOrId(WhenInitializingPerson):

    allowed_exceptions = Exception

    @classmethod
    def arrange(cls):
        super(WhenInitializingPersonWithoutDisplayNameOrId, cls).arrange()
        del cls.kwargs['display_name']
        del cls.kwargs['person_id']

    def should_raise_assertion_error(self):
        self.assertIsInstance(self.exception, AssertionError)


class WhenInitializingPersonWithDisplayName(WhenInitializingPerson):

    @classmethod
    def arrange(cls):
        super(WhenInitializingPersonWithDisplayName, cls).arrange()
        del cls.kwargs['person_id']

    def should_save_display_name(self):
        self.assertEqual(self.person.display_name, sentinel.display_name)

    def should_not_have_id(self):
        self.assertIsNone(self.person.id)


class WhenInitializingPersonWithId(WhenInitializingPerson):

    @classmethod
    def arrange(cls):
        super(WhenInitializingPersonWithId, cls).arrange()
        del cls.kwargs['display_name']

    def should_save_id(self):
        self.assertEqual(self.person.id, sentinel.person_id)


###############################################################################
### Person.as_dictionary
###############################################################################

class WhenConvertingToDictionary(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenConvertingToDictionary, cls).arrange()
        cls.person = Person(
            display_name=sentinel.display_name,
            person_id=sentinel.person_id,
        )

    @classmethod
    def act(cls):
        cls.dict_repr = cls.person.as_dictionary()

    def should_populate_id(self):
        self.assertEqual(self.dict_repr['id'], sentinel.person_id)

    def should_populate_display_name(self):
        self.assertEqual(self.dict_repr['display_name'], sentinel.display_name)

    def should_populate_events_list(self):
        self.assertEqual(self.dict_repr['events'], self.person.events)


###############################################################################
### Person.from_dictionary
###############################################################################

class FromDictionaryTestCase(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(FromDictionaryTestCase, cls).arrange()
        cls.dict_repr = {
            'display_name': sentinel.display_name,
            'id': sentinel.person_id,
            'events': [sentinel.event],
        }

    @classmethod
    def act(cls):
        cls.person = Person.from_dictionary(cls.dict_repr)


class WhenConvertingFromDictionary(FromDictionaryTestCase):

    def should_populate_id(self):
        self.assertEqual(self.person.id, self.dict_repr['id'])

    def should_populate_display_name(self):
        self.assertEqual(
            self.person.display_name, self.dict_repr['display_name'])

    def should_populate_events(self):
        self.assertEqual(self.person.events, [sentinel.event])


class WhenConvertingFromDictionaryWithoutDisplayName(FromDictionaryTestCase):
    allowed_exceptions = KeyError

    @classmethod
    def arrange(cls):
        super(WhenConvertingFromDictionaryWithoutDisplayName, cls).arrange()
        del cls.dict_repr['display_name']

    def should_raise_key_error(self):
        self.assertIsInstance(self.exception, KeyError)


class WhenConvertingFromDictionaryWithoutId(FromDictionaryTestCase):

    @classmethod
    def arrange(cls):
        super(WhenConvertingFromDictionaryWithoutId, cls).arrange()
        del cls.dict_repr['id']

    def should_populate_display_name(self):
        self.assertEqual(
            self.person.display_name, self.dict_repr['display_name'])


###############################################################################
### Person.add_event
###############################################################################

class WhenAddingEvent(fluenttest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenAddingEvent, cls).arrange()
        cls.person = Person(sentinel.display_name)
        cls.person.events = Mock()

    @classmethod
    def act(cls):
        cls.person.add_event(sentinel.event_url)

    def should_append_new_event(self):
        self.person.events.append(sentinel.event_url)


###############################################################################
### Person.remove_event
###############################################################################

class WhenRemovingEvent(fluenttest.TestCase):

    @classmethod
    def arrange(cls):
        super(WhenRemovingEvent, cls).arrange()
        cls.person = Person(sentinel.display_name)
        cls.person.events = Mock()

    @classmethod
    def act(cls):
        cls.person.remove_event(sentinel.event_url)

    def should_remove_event_url(self):
        self.person.events.remove.assert_called_once_with(sentinel.event_url)
