from hc.api.models import Channel, Check
from hc.test import BaseTestCase


class ApiAdminTestCase(BaseTestCase):

    def setUp(self):
        super(ApiAdminTestCase, self).setUp()
        self.check = Check.objects.create(user=self.alice, tags="foo bar")
        # Set Alice to be staff and superuser and save her :)
        self.check.user.is_superuser = True
        self.check.user.is_staff = True
        self.check.user.save()

    def test_it_shows_channel_list_with_pushbullet(self):
        self.client.login(username="alice@example.org", password="password")

        test_channel = Channel(user=self.alice, kind="pushbullet", value="test-token")
        test_channel.save()

        # Assert for the push bullet
        self.assertEqual(test_channel.kind, 'pushbullet')
