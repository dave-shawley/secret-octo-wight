from familytree import main
from ..helpers import tornado


class EntityActionMixin(object):

    """Add methods that improve test entities with actions."""

    @classmethod
    def perform_action(cls, target, action_name, wants_json=True, *args):
        """Perform an action by following its link.

        :param dict target: the entity to act upon
        :param str action_name: the action to perform
        :param bool wants_json: should the JSONified HTTP
            helper be used?
        :param *args: parameters that are passed through

        This method looks up ``action`` in the target's action
        card and fires the action.  For example, if you want to
        create and remove a person, you could do the following::

            person = cls.make_person(details)
            cls.delete(person['actions']['delete-person'])

        But that assumes the HTTP method that the particular
        action is implemented by.  Instead, this method will
        take care of determining the correct HTTP method and
        URL for you.

        """
        action_map = {
            'GET': (cls.get_json, cls.http_get),
            'POST': (cls.post_json, cls.http_post),
            'DELETE': (cls.http_delete, cls.http_delete),
        }

        assert action_name in target['actions']
        action = target['actions'][action_name]
        try:
            json_method, generic_method = action_map[action['method']]
        except KeyError:  # pragma: no cover
            raise RuntimeError(
                '{0} is not a known HTTP method'.format(action['method']))

        method = json_method if wants_json else generic_method
        return method(action['url'], *args)

    def assert_has_action(self, target, action_name):
        self.assertIn(action_name, target['actions'])


class AcceptanceTestCase(
        EntityActionMixin, tornado.JSONMixin, tornado.TornadoTestCase):

    """Test case for acceptance tests.

    This class is a basic test case that provides functionality
    useful for writing acceptance tests against the JSON/HTTP API.

    """

    @classmethod
    def make_application(cls):
        return main.Application()

    @classmethod
    def make_person(cls, **body):
        """Create a Person instance

        :param body: values to pass in the JSON document to create
            the new person
        :return: the JSON response

        """
        return cls.post_json('person', body)

    @classmethod
    def make_event(cls, **body):
        """Create a Event instance.

        :param body: values to pass in the JSON document to create
            the new event
        :return: the JSON response

        """
        return cls.post_json('event', body)
