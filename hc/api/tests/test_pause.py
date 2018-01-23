from django.urls import reverse
from hc.api.models import Check
from hc.test import BaseTestCase


class PauseTestCase(BaseTestCase):

    def test_it_works(self):
        check = Check(user=self.alice, status="up")
        check.save()

        url = reverse("hc-api-pause", args=[check.code])
        response = self.client.post(
            url, "", content_type="application/json",
            HTTP_X_API_KEY="abc"
        )

        ### Assert the expected status code and check's status
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'paused')

    def test_it_validates_ownership(self):
        check = Check(user=self.bob, status="up")
        check.save()

        url = reverse("hc-api-pause", args=[check.code])
        response = self.client.post(
            url, "", content_type="application/json",
            HTTP_X_API_KEY="abc"
        )

        self.assertEqual(response.status_code, 400)

    def test_it_only_allows_post_requests(self):
        """
        This test asserts that only the POST HTTP method
        is allowed on this resource.
        """
        check = Check(user=self.bob, status="up")
        check.save()

        ### Test that it only allows post requests
        url = reverse("hc-api-pause", args=[check.code])
        response_one = self.client.get(
            url, "", content_type="application/json",
            HTTP_X_API_KEY="abc"
        )

        response_two = self.client.put(
            url, "", content_type="application/json",
            HTTP_X_API_KEY="abc"
        )

        response_three = self.client.delete(
            url, "", content_type="application/json",
            HTTP_X_API_KEY="abc"
        )

        self.assertEqual(response_one.status_code, 405)
        self.assertEqual(response_two.status_code, 405)
        self.assertEqual(response_three.status_code, 405)
