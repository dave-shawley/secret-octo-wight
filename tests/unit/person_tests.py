import unittest

from mock import ANY, Mock, sentinel
import fluenttest

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

    def should_save_model_instance(self):
        self.person.save.assert_called_once_with()

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

class WhenPersonHandlerGets(TornadoHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenPersonHandlerGets, cls).arrange()
        cls.data_store = cls.patch('familytree.person.PEOPLE')
        cls.person_class = cls.patch('familytree.person.Person')
        cls.person = cls.data_store.__getitem__.return_value
        cls.handler = PersonHandler(cls.application, cls.request)
        cls.handler.serialize_model_instance = Mock()

    @classmethod
    def act(cls):
        cls.response = cls.handler.get(sentinel.person_id)

    def should_retrieve_person_from_data_store(self):
        self.data_store.__getitem__.assert_called_once_with(sentinel.person_id)

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


###############################################################################
### Person.__init__
###############################################################################

class WhenInitializingPersonWithoutDisplayNameOrId(
        fluenttest.TestCase, unittest.TestCase):

    allowed_exceptions = Exception

    @classmethod
    def act(cls):
        Person()

    def should_raise_assertion_error(self):
        self.assertIsInstance(self.exception, AssertionError)


class WhenInitializingPersonWithDisplayName(
        fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def act(cls):
        cls.person = Person(display_name=sentinel.display_name)

    def should_save_display_name(self):
        self.assertEqual(self.person.display_name, sentinel.display_name)

    def should_not_have_id(self):
        self.assertIsNone(self.person.id)


class WhenInitializingPersonWithId(fluenttest.TestCase, unittest.TestCase):

    @classmethod
    def act(cls):
        cls.person = Person(person_id=sentinel.id)

    def should_save_id(self):
        self.assertEqual(self.person.id, sentinel.id)


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
