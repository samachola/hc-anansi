from django.contrib.auth.models import User
from django.test import TestCase
from hc.accounts.models import Profile


class TeamAccessMiddlewareTestCase(TestCase):

    def test_it_handles_missing_profile(self):
        """ Ensure that when a user is created without a profile,
        then the middleware creates a profile when he passes through login"""
        # create a user without profile
        user = User(username="ned", email="ned@example.org")
        user.set_password("password")
        user.save()

        # login the user, and go to the about page
        # hence calling middleware
        self.client.login(username="ned@example.org", password="password")
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)

        # Assert the new Profile objects count
        profiles = list(Profile.objects.all())
        assert profiles