from __future__ import print_function

import httplib
import unittest

from familytree.main import Application
from ..helpers.tornado import JSONMixin, TornadoTestCase


class PersonApiTestCase(TornadoTestCase):
    @classmethod
    def make_application(cls):
        return Application()


class PersonApiMixin(JSONMixin):
    @classmethod
    def arrange(cls):
        super(PersonApiMixin, cls).arrange()
        cls.request_body = {
            'display_name': 'display name',
        }


class WhenCreatingPersonWithoutBody(PersonApiTestCase):
    @classmethod
    def act(cls):
        cls.response = cls.post(cls.build_request('person', body=''))

    def should_fail_with_bad_request(self):
        self.assertEquals(self.response.code, httplib.BAD_REQUEST)


class WhenCreatingPersonWithoutDisplayName(PersonApiMixin, PersonApiTestCase):
    @classmethod
    def arrange(cls):
        super(WhenCreatingPersonWithoutDisplayName, cls).arrange()
        del cls.request_body['display_name']

    @classmethod
    def act(cls):
        cls.response = cls.post_json('person', cls.request_body)

    def should_fail_with_bad_request(self):
        self.assertEquals(self.last_response.code, httplib.BAD_REQUEST)


class WhenCreatingPersonWithUnrecognizedContentType(PersonApiTestCase):
    @classmethod
    def act(cls):
        cls.response = cls.post(cls.build_request(
            'person',
            headers={'Content-Type': 'application/vnd.does.not.exist'},
            body='Random Gibberish',
        ))

    def should_fail_with_invalid_content_type(self):
        self.assertEquals(
            self.last_response.code, httplib.UNSUPPORTED_MEDIA_TYPE)


class WhenCreatingPerson(PersonApiMixin, PersonApiTestCase):
    @classmethod
    def act(cls):
        cls.response = cls.post_json('person', cls.request_body)

    def should_return_created_status(self):
        self.assertEquals(self.last_response.code, httplib.CREATED)

    def should_return_person_with_display_name(self):
        self.assertEquals(self.response['display_name'], 'display name')

    def should_include_self_link(self):
        self.assertIn('self', self.response)

    def should_include_self_link_as_location_header(self):
        self.assertEquals(
            self.last_response.headers['Location'],
            self.response['self'],
        )


class WhenFetchingCreatedPerson(PersonApiMixin, PersonApiTestCase):
    @classmethod
    def arrange(cls):
        super(WhenFetchingCreatedPerson, cls).arrange()
        cls.person = cls.post_json('person', cls.request_body)

    @classmethod
    def act(cls):
        cls.response = cls.get_json(cls.person['self'])

    def should_return_ok_status(self):
        self.assertEquals(self.last_response.code, httplib.OK)

    def should_return_same_person(self):
        self.assertEquals(self.response, self.person)


class WhenFetchingPerson(PersonApiMixin, PersonApiTestCase):
    @classmethod
    def arrange(cls):
        super(WhenFetchingPerson, cls).arrange()
        response = cls.post_json('person', cls.request_body)
        cls.person_url = cls.last_response.headers['Location']

    @classmethod
    def act(cls):
        cls.response = cls.get_json(cls.person_url)

    def should_return_ok_status(self):
        self.assertEquals(self.last_response.code, httplib.OK)

    def should_include_self_link(self):
        self.assertEquals(self.response['self'], self.person_url)

    def should_include_delete_person_action(self):
        self.assertDictContainsSubset(
            {'method': 'DELETE'},
            self.response['actions']['delete-person'],
        )
