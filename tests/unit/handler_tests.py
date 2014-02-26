import unittest

from fluenttest import TestCase
from mock import sentinel, Mock, MagicMock, PropertyMock
from tornado.web import HTTPError

from familytree.handlers import BaseHandler
from . import TornadoHandlerTestCase


class BaseHandlerTestCase(TornadoHandlerTestCase, unittest.TestCase):

    @classmethod
    def arrange(cls):
        super(BaseHandlerTestCase, cls).arrange()
        cls._header_contents = {}
        cls.request.headers = Mock()
        cls.request.headers.get.side_effect = cls._header_contents.get

        cls.handler = BaseHandler(cls.application, cls.request)


###############################################################################
### BaseHandler.get_url_for
###############################################################################

class WhenGettingUrlFromBaseHandler(BaseHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenGettingUrlFromBaseHandler, cls).arrange()
        cls.args = (sentinel.arg1, sentinel.arg2)

    @classmethod
    def act(cls):
        cls.returned = cls.handler.get_url_for(sentinel.handler, *cls.args)

    def should_get_url_from_application(self):
        self.application.get_url_for.assert_called_once_with(
            self.request,
            sentinel.handler,
            *self.args
        )


###############################################################################
### BaseHandler.require_request_body
###############################################################################

class RequireRequestBodyTestCase(BaseHandlerTestCase):
    allowed_exceptions = HTTPError

    @classmethod
    def act(cls):
        cls.handler.require_request_body()

    @classmethod
    def set_request_body(cls, body):
        cls.request.body = body
        cls._header_contents['Content-Length'] = str(len(body))


class WhenRequiringRequestBodyWithBody(RequireRequestBodyTestCase):

    @classmethod
    def arrange(cls):
        super(WhenRequiringRequestBodyWithBody, cls).arrange()
        cls.set_request_body('some body')

    def should_not_raise(self):
        self.assertIsNone(self.exception)


class WhenRequiringRequestBodyWithEmptyBody(RequireRequestBodyTestCase):

    @classmethod
    def arrange(cls):
        super(WhenRequiringRequestBodyWithEmptyBody, cls).arrange()
        # HTTPRequest sets body to empty string in initializer if None
        cls.set_request_body('')

    def should_raise_http_error(self):
        self.assertIsInstance(self.exception, HTTPError)

    def should_raise_bad_request(self):
        self.assertEquals(self.exception.status_code, 400)


class WhenRequiringRequestBodyWithoutContentLength(RequireRequestBodyTestCase):

    def should_examine_content_length_header(self):
        self.request.headers.get.assert_any_call('Content-Length', '0')

    def should_raise_http_error(self):
        self.assertIsInstance(self.exception, HTTPError)

    def should_raise_bad_request(self):
        self.assertEqual(self.exception.status_code, 400)


###############################################################################
### BaseHandler.serialize_model_instance
###############################################################################

class _SerializeModelInstanceTestCase(BaseHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(_SerializeModelInstanceTestCase, cls).arrange()
        cls.model_instance = Mock()
        cls.model_representation = MagicMock()
        cls.json_dumps = cls.patch('familytree.handlers.json').dumps
        cls.handler.set_header = Mock()
        cls.handler.write = Mock()
        cls.model_instance.as_dictionary.return_value = (
            cls.model_representation)

    def should_convert_instance_to_dictionary(self):
        self.model_instance.as_dictionary.assert_called_once_with()

    def should_dump_dictionary_as_json(self):
        self.json_dumps.assert_called_once_with(self.model_representation)

    def should_set_content_type_header(self):
        self.handler.set_header.assert_any_call(
            'Content-Type', 'application/json')

    def should_write_serialized_instance(self):
        self.handler.write.assert_called_once_with(
            self.json_dumps.return_value)


class WhenSerializingModelInstance(_SerializeModelInstanceTestCase):

    @classmethod
    def act(cls):
        cls.returned = cls.handler.serialize_model_instance(cls.model_instance)


class WhenSerializingModelInstanceWithHandlerSpecified(
        _SerializeModelInstanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenSerializingModelInstanceWithHandlerSpecified, cls).arrange()
        cls.model_handler = Mock()
        cls.handler.get_url_for = Mock()

    @classmethod
    def act(cls):
        cls.returned = cls.handler.serialize_model_instance(
            cls.model_instance, model_handler=cls.model_handler)

    def should_generate_canonical_url(self):
        self.handler.get_url_for.assert_called_with(
            self.model_handler,
            self.model_representation['id'],
        )

    def should_store_canonical_url_in_location(self):
        self.handler.set_header.assert_any_call(
            'Location',
            self.handler.get_url_for.return_value,
        )

    def should_set_self_link_in_representation(self):
        self.model_representation.__setitem__.assert_any_call(
            'self', self.handler.get_url_for.return_value,
        )


class WhenSerializingModelInstanceWithActions(_SerializeModelInstanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenSerializingModelInstanceWithActions, cls).arrange()
        cls.action_dict = {
            'name': sentinel.action_name,
            'method': sentinel.action_method,
            'handler': sentinel.action_handler,
            'args': (sentinel.arg1, sentinel.arg2,),
        }
        cls.action = MagicMock()
        cls.action.__getitem__.side_effect = cls.action_dict.get
        cls.handler.get_url_for = Mock()
        cls.action_card = cls.model_representation.setdefault.return_value

    @classmethod
    def act(cls):
        cls.returned = cls.handler.serialize_model_instance(
            cls.model_instance, MagicMock(), MagicMock(), cls.action)

    def should_create_action_card(self):
        self.model_representation.setdefault.assert_any_call('actions', {})

    def should_extract_name_from_action(self):
        self.action.__getitem__.assert_any_call('name')

    def should_extract_method_from_action(self):
        self.action.__getitem__.assert_any_call('method')

    def should_extract_handler_from_action(self):
        self.action.__getitem__.assert_any_call('handler')

    def should_extract_args_from_action(self):
        self.action.__getitem__.assert_any_call('args')

    def should_get_url_for_action(self):
        self.handler.get_url_for.assert_any_call(
            self.action_dict['handler'],
            *self.action_dict['args']
        )

    def should_add_action_to_representation(self):
        self.action_card.__setitem__.assert_any_call(
            self.action_dict['name'],
            {
                'method': self.action_dict['method'],
                'url': self.handler.get_url_for.return_value,
            },
        )


###############################################################################
### BaseHandler.deserialize_model_instance
###############################################################################

class WhenDeserializingModelInstance(BaseHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(WhenDeserializingModelInstance, cls).arrange()
        cls.model_class = Mock()
        cls.request_body_property = cls.patch(
            'familytree.handlers.BaseHandler.request_body',
            new_callable=PropertyMock,
        )

    @classmethod
    def act(cls):
        cls.instance = cls.handler.deserialize_model_instance(cls.model_class)

    def should_create_model_from_request_body(self):
        self.model_class.from_dictionary.assert_called_once_with(
            self.request_body_property)

    def should_return_model_instance(self):
        self.assertEqual(
            self.instance, self.model_class.from_dictionary.return_value)


###############################################################################
### BaseHandler.request_body
###############################################################################

class _RequestBodyTestCase(BaseHandlerTestCase):

    @classmethod
    def arrange(cls):
        super(_RequestBodyTestCase, cls).arrange()
        cls.content_type = Mock()
        cls._header_contents['Content-Length'] = 'non-zero value'
        cls._header_contents['Content-Type'] = cls.content_type

        cls.handler.require_request_body = Mock()

        cls.supported_media_types = MagicMock()
        cls.handler.supported_media_types = cls.supported_media_types

    @classmethod
    def act(cls):
        cls.returned = cls.handler.request_body

    def should_require_request_body(self):
        self.handler.require_request_body.assert_called_once_with()

    def should_verify_that_content_type_is_supported(self):
        self.supported_media_types.__contains__.assert_called_once_with(
            self.content_type)


class WhenGeneratingRequestBodyFromJson(_RequestBodyTestCase):

    @classmethod
    def arrange(cls):
        super(WhenGeneratingRequestBodyFromJson, cls).arrange()
        cls.json_loads = cls.patch('familytree.handlers.json').loads
        cls.supported_media_types.__contains__.return_value = True
        cls.content_type.startswith.return_value = True

    def should_check_for_json_content_type(self):
        self.content_type.startswith.assert_any_call('application/json')

    def should_load_json_body(self):
        self.json_loads.assert_called_once_with(self.handler.request.body)

    def should_return_json_result(self):
        self.assertEqual(self.returned, self.json_loads.return_value)


class WhenGeneratingRequestBodyFromUnsupportedType(_RequestBodyTestCase):
    allowed_exceptions = HTTPError

    @classmethod
    def arrange(cls):
        super(WhenGeneratingRequestBodyFromUnsupportedType, cls).arrange()
        cls.supported_media_types.__contains__.return_value = False

    def should_raise_http_error(self):
        self.assertIsInstance(self.exception, HTTPError)

    def should_raise_unsupported_media_type(self):
        self.assertEqual(self.exception.status_code, 415)


class WhenGeneratingRequestBodyFromUnimplementedType(_RequestBodyTestCase):
    allowed_exceptions = HTTPError

    @classmethod
    def arrange(cls):
        super(WhenGeneratingRequestBodyFromUnimplementedType, cls).arrange()
        cls.supported_media_types.__contains__.return_value = True
        cls.content_type.startswith.return_value = False

    def should_raise_http_error(self):
        self.assertIsInstance(self.exception, HTTPError)

    def should_raise_internal_server_error(self):
        self.assertEqual(self.exception.status_code, 500)

    def should_include_reason_in_exception(self):
        self.assertIsNotNone(self.exception.reason)

    def should_include_log_message_mentioning_content_type(self):
        self.assertIn(
            str(self.content_type),
            self.exception.log_message,
        )


class WhenGeneratingRequestBodySecondTime(_RequestBodyTestCase):

    @classmethod
    def arrange(cls):
        super(WhenGeneratingRequestBodySecondTime, cls).arrange()
        cls.json_loads = cls.patch('familytree.handlers.json').loads
        cls.supported_media_types.__contains__.return_value = True
        cls.content_type.startswith.return_value = True

    @classmethod
    def act(cls):
        cls.returned = cls.handler.request_body
        cls.second_returned = cls.handler.request_body

    def should_return_same_value(self):
        self.assertIs(self.returned, self.second_returned)
