from django.contrib.auth.hashers import make_password
from hc.test import BaseTestCase
from django.urls import reverse


class CheckTokenTestCase(BaseTestCase):

    def setUp(self):
        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        r = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(r, "You are about to log in")

    def test_it_redirects(self):
        r = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(r, "/checks/")

        # After login, token should be blank
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    def test_login_redirects_when_already_logged_in(self):
        """ Ensure that when a logged in user visits login page,
        he is redirected to his profile page
        """
        # login
        url = reverse('hc-check-token', args=['alice', 'secret-token'])
        response = self.client.post(url)
        self.assertRedirects(response, "/checks/")

        # logging in again should redirect to checks
        response = self.client.get(url)
        self.assertRedirects(response, "/checks/")

    def test_login_redirects_with_a_bad_token(self):
        """ Ensure that when a bad token is provided for logging in,
        then it should redirect to the login page 
        """
        url = reverse('hc-check-token', args=['alice', 'bad-token'])
        response = self.client.post(url)
        
        self.assertRedirects(response, "/accounts/login/")

    def test_login_redirects_with_a_wrong_name(self):
        """ Ensure that when a bad username is provided for logging in,
        then it should redirect to the login page
        """
        url = reverse('hc-check-token', args=['wrong-name', 'secret-token'])
        response = self.client.post(url)
        
        self.assertRedirects(response, "/accounts/login/")

    def test_login_redirects_to_login_with_previous_login_link(self):
        """ Ensure that it redirects to login page,
        when the login token is used and the user logs out
        and tries to login again using the same token
        """
        login_url = reverse('hc-check-token', args=['alice', 'secret-token'])
        logout_url = reverse('hc-logout')

        # login and check if it works
        response = self.client.post(login_url)
        self.assertRedirects(response, "/checks/")

        # logout and check if it redirects to index page
        response = self.client.post(logout_url)
        self.assertRedirects(response, "/")

        # try logging again using the same token and
        # check if it correctly redirects to login
        response = self.client.post(login_url)
        self.assertRedirects(response, "/accounts/login/")


