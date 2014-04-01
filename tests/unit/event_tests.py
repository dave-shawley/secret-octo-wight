from tornado import web

from familytree import event
from familytree import person
from . import TornadoHandlerTestCase
from ..helpers.compat import mock
from ..helpers.compat import unittest


###############################################################################
### CreateEventHandler.post
###############################################################################

class CreateEventHandlerTestCase(TornadoHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(CreateEventHandlerTestCase, cls).arrange()
        cls.storage = cls.patch('familytree.event.storage')
        cls.uuid_module = cls.patch('familytree.event.uuid')
        cls.handler = event.CreateEventHandler(cls.application, cls.request)
        cls.handler.deserialize_model_instance = mock.Mock()
        cls.handler.serialize_model_instance = mock.Mock()
        cls.handler.set_status = mock.Mock()

    @classmethod
    def act(cls):
        cls.response = cls.handler.post()

    def should_deserialize_model_instance(self):
        self.handler.deserialize_model_instance.assert_called_once_with(
            event.Event)

    def should_generate_event_id(self):
        self.uuid_module.uuid4.assert_called_once_with()

    def should_save_model_instance(self):
        self.storage.save_item.assert_any_call(
            self.handler.deserialize_model_instance.return_value,
            self.uuid_module.uuid4.return_value.hex,
        )

    def should_serialize_model_instance(self):
        self.handler.serialize_model_instance.assert_called_once_with(
            self.handler.deserialize_model_instance.return_value,
            mock.ANY,
            model_handler=event.EventHandler,
        )

    def should_set_status_to_created(self):
        self.handler.set_status.assert_called_once_with(201)


class WhenPostingToCreateEventHandler(CreateEventHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenPostingToCreateEventHandler, cls).arrange()
        an_event = cls.handler.deserialize_model_instance.return_value
        an_event.people = []


class WhenPostingToCreateEventHandlerWithPeople(CreateEventHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenPostingToCreateEventHandlerWithPeople, cls).arrange()
        cls.handler.get_url_for = mock.Mock()
        cls.person_url = mock.Mock()
        cls.person_url.split.return_value = [
            mock.sentinel.path, mock.sentinel.person_id]
        an_event = cls.handler.deserialize_model_instance.return_value
        an_event.people = [cls.person_url]
        cls.person = cls.storage.get_item.return_value

    def should_extract_id_from_person_url(self):
        self.person_url.split.assert_called_once_with('/')

    def should_retrieve_person_from_storage(self):
        self.storage.get_item.assert_called_once_with(
            person.Person, mock.sentinel.person_id)

    def should_fetch_url_for_event(self):
        self.handler.get_url_for.assert_called_once_with(
            event.EventHandler, self.uuid_module.uuid4.return_value.hex)

    def should_add_event_to_person(self):
        self.person.add_event.assert_called_once_with(
            self.handler.get_url_for.return_value)

    def should_save_modified_person(self):
        self.storage.save_item.assert_any_call(self.person, self.person.id)


###############################################################################
### EventHandler.get
###############################################################################

class WhenEventHandlerGets(TornadoHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenEventHandlerGets, cls).arrange()
        cls.storage = cls.patch('familytree.event.storage')
        cls.event = cls.storage.get_item.return_value
        cls.handler = event.EventHandler(cls.application, cls.request)
        cls.handler.serialize_model_instance = mock.Mock()
        cls.handler.set_status = mock.Mock()

    @classmethod
    def act(cls):
        cls.response = cls.handler.get(mock.sentinel.event_id)

    def should_retrieve_event_from_data_store(self):
        self.storage.get_item.assert_called_once_with(
            event.Event, mock.sentinel.event_id)

    def should_serialize_model_instance(self):
        self.handler.serialize_model_instance.assert_called_once_with(
            self.event,
            mock.ANY,
            model_handler=event.EventHandler,
        )

    def should_set_status_to_ok(self):
        self.handler.set_status.assert_called_once_with(200)


###############################################################################
### EventHandler.delete
###############################################################################

class EventHandlerDeleteTestCase(TornadoHandlerTestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(EventHandlerDeleteTestCase, cls).arrange()
        cls.storage = cls.patch('familytree.event.storage')
        cls.target_event = mock.Mock()
        cls.target_event.people = []
        cls.get_item_returns = [cls.target_event]
        cls.storage.get_item.side_effect = cls.get_item_returns
        cls.handler = event.EventHandler(cls.application, cls.request)

    @classmethod
    def act(cls):
        cls.response = cls.handler.delete(mock.sentinel.event_id)

    def should_retrieve_event_from_data_store(self):
        self.storage.get_item.assert_any_call(
            event.Event, mock.sentinel.event_id)

    def should_delete_item_from_data_store(self):
        self.storage.delete_item.assert_called_once_with(
            event.Event, mock.sentinel.event_id)


class WhenEventHandlerDeletes(EventHandlerDeleteTestCase):

    @classmethod
    def arrange(cls):
        super(WhenEventHandlerDeletes, cls).arrange()
        cls.handler.set_status = mock.Mock()

    def should_set_status_to_no_content(self):
        self.handler.set_status.assert_called_once_with(204)


class WhenEventHandlerDeletesMissingItem(EventHandlerDeleteTestCase):

    allowed_exceptions = Exception

    @classmethod
    def arrange(cls):
        super(WhenEventHandlerDeletesMissingItem, cls).arrange()
        cls.storage.InstanceNotFound = RuntimeError
        cls.storage.delete_item.side_effect = RuntimeError

    def should_raise_http_error(self):
        self.assertIsInstance(self.exception, web.HTTPError)

    def should_raise_not_found(self):
        self.assertEqual(self.exception.status_code, 404)


class WhenEventHandlerDeletesItemWithPeople(EventHandlerDeleteTestCase):

    @classmethod
    def arrange(cls):
        super(WhenEventHandlerDeletesItemWithPeople, cls).arrange()
        cls.person = mock.Mock()
        cls.get_item_returns.append(cls.person)

        cls.person_url = mock.Mock()
        cls.person_url.rsplit.return_value = [
            mock.sentinel.path, mock.sentinel.id]
        cls.target_event.people.append(cls.person_url)

    def should_extract_id_from_person_url(self):
        self.person_url.rsplit.assert_called_once_with('/', 1)

    def should_retrieve_person_from_data_store(self):
        self.storage.get_item.assert_any_call(person.Person, mock.sentinel.id)

    def should_remove_event_from_person(self):
        self.person.remove_event.assert_called_once_with(
            self.request.full_url.return_value)

    def should_save_modified_person(self):
        self.storage.save_item.assert_called_once_with(
            self.person, self.person.id)
