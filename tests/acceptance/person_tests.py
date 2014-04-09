from ..helpers import tornado
from . import AcceptanceTestCase
import familytree.main


class PersonApiTestCase(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(PersonApiTestCase, cls).arrange()
        cls.request_body = {
            'display_name': 'display name',
        }


class WhenCreatingPersonWithoutBody(tornado.TornadoTestCase):

    @classmethod
    def make_application(cls):
        return familytree.main.Application()

    @classmethod
    def act(cls):
        cls.response = cls.http_post(cls.build_request('person', body=''))

    def should_fail_with_bad_request(self):
        self.assertEqual(self.response.code, 400)


class WhenCreatingPersonWithoutDisplayName(PersonApiTestCase):

    @classmethod
    def arrange(cls):
        super(WhenCreatingPersonWithoutDisplayName, cls).arrange()
        del cls.request_body['display_name']

    @classmethod
    def act(cls):
        cls.response = cls.post_json('person', cls.request_body)

    def should_fail_with_bad_request(self):
        self.assertEqual(self.last_response.code, 400)


class WhenCreatingPersonWithUnrecognizedContentType(tornado.TornadoTestCase):

    @classmethod
    def make_application(cls):
        return familytree.main.Application()

    @classmethod
    def act(cls):
        cls.response = cls.http_post(cls.build_request(
            'person',
            headers={'Content-Type': 'application/vnd.does.not.exist'},
            body='Random Gibberish',
        ))

    def should_fail_with_invalid_content_type(self):
        self.assertEqual(
            self.last_response.code, 415)


class WhenCreatingPerson(PersonApiTestCase):

    @classmethod
    def act(cls):
        cls.response = cls.post_json('person', cls.request_body)

    def should_return_created_status(self):
        self.assertEqual(self.last_response.code, 201)

    def should_return_person_with_display_name(self):
        self.assertEqual(self.response['display_name'], 'display name')

    def should_include_self_link(self):
        self.assertIn('self', self.response)

    def should_include_self_link_as_location_header(self):
        self.assertEqual(
            self.last_response.headers['Location'],
            self.response['self'],
        )


class WhenFetchingCreatedPerson(PersonApiTestCase):

    @classmethod
    def arrange(cls):
        super(WhenFetchingCreatedPerson, cls).arrange()
        cls.person = cls.make_person(display_name='display name')
        cls.person_url = cls.person['self']

    @classmethod
    def act(cls):
        cls.response = cls.get_json(cls.person_url)

    def should_return_ok_status(self):
        self.assertEqual(self.last_response.code, 200)

    def should_return_created_person(self):
        self.assertEqual(self.response, self.person)

    def should_include_self_link(self):
        self.assertEqual(self.response['self'], self.person_url)

    def should_include_location_header(self):
        self.assertEqual(
            self.last_response.headers['Location'], self.person_url)

    def should_include_delete_person_action(self):
        self.assertIn('delete-person', self.response['actions'])


class WhenDeletingPerson(PersonApiTestCase):

    @classmethod
    def arrange(cls):
        super(WhenDeletingPerson, cls).arrange()
        cls.person = cls.make_person(display_name='display name')

    @classmethod
    def act(cls):
        cls.response = cls.http_delete(
            cls.person['actions']['delete-person']['url'])

    def should_return_no_content(self):
        self.assertEqual(self.response.code, 204)

    def should_return_not_found_after_delete(self):
        response = self.http_get(self.person['self'])
        self.assertEqual(response.code, 404)
