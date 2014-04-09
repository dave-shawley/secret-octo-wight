from . import AcceptanceTestCase


class WhenCreatingFamily(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenCreatingFamily, cls).arrange()
        cls.first_person = cls.make_person(display_name='person one')
        cls.second_person = cls.make_person(display_name='person two')

    @classmethod
    def act(cls):
        cls.event = cls.post_json('event', {
            'type': 'family',
            'people': [
                cls.first_person['self'],
                cls.second_person['self'],
            ],
        })

    def should_return_created(self):
        self.assertEqual(self.last_response.code, 201)

    def should_return_self_link(self):
        self.assertIn('self', self.event)

    def should_include_self_link_as_location_header(self):
        self.assertEqual(
            self.last_response.headers['Location'], self.event['self'])


class WhenFetchingCreatedEvent(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenFetchingCreatedEvent, cls).arrange()
        cls.first_person = cls.make_person(display_name='person one')
        cls.second_person = cls.make_person(display_name='person two')
        event = cls.make_event(
            type='family',
            people=[cls.first_person['self'], cls.second_person['self']],
        )
        cls.event_url = event['self']

    @classmethod
    def act(cls):
        cls.event = cls.get_json(cls.event_url)

    def should_return_ok_status(self):
        self.assertEqual(self.last_response.code, 200)

    def should_include_self_link(self):
        self.assertEqual(self.event['self'], self.event_url)

    def should_include_links_to_people(self):
        self.assertIn(self.first_person['self'], self.event['people'])
        self.assertIn(self.second_person['self'], self.event['people'])

    def should_include_delete_event_action(self):
        self.assertIn('delete-event', self.event['actions'])


class WhenEventIsCreatedRelatedPeopleAreModified(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenEventIsCreatedRelatedPeopleAreModified, cls).arrange()
        person = cls.make_person(display_name='a person')
        cls.person_url = person['self']
        event = cls.make_event(type='family', people=[person['self']])
        cls.event_url = event['self']

    @classmethod
    def act(cls):
        cls.person = cls.get_json(cls.person_url)

    def should_include_event(self):
        self.assertIn(self.event_url, self.person['events'])


class WhenDeletingFamilyEvent(AcceptanceTestCase):

    @classmethod
    def arrange(cls):
        super(WhenDeletingFamilyEvent, cls).arrange()
        person = cls.make_person(display_name='a person')
        cls.person_url = person['self']
        event = cls.make_event(type='family', people=[cls.person_url])
        cls.event_url = event['self']

    @classmethod
    def act(cls):
        cls.response = cls.http_delete(cls.event_url)

    def should_return_no_content(self):
        self.assertEqual(self.response.code, 204)

    def should_delete_event(self):
        response = self.http_get(self.event_url)
        self.assertEqual(response.code, 404)

    def should_remove_event_from_people(self):
        person = self.get_json(self.person_url)
        self.assertEqual(len(person['events']), 0)
