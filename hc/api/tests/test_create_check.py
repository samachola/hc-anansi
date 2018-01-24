import json
from django.urls import reverse
from hc.api.models import Channel, Check
from hc.api import views
from hc.test import BaseTestCase


class CreateCheckTestCase(BaseTestCase):
    URL = reverse('hc-api-checks')

    def setUp(self):
        super(CreateCheckTestCase, self).setUp()

    def post(self, data, expected_error=None):
        response = self.client.post(
            self.URL, json.dumps(data),
            content_type="application/json"
        )

        if expected_error:
            self.assertEqual(response.status_code, 400)
            ### Assert that the expected error is the response error
            response_payload = response.json()
            self.assertEqual(response_payload["error"], expected_error)

        return response

    def test_it_works(self):
        r = self.post({
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 3600,
            "grace": 60
        })

        self.assertEqual(r.status_code, 201)

        doc = r.json()
        assert "ping_url" in doc
        self.assertEqual(doc["name"], "Foo")
        self.assertEqual(doc["tags"], "bar,baz")
        ### Assert the expected last_ping and n_pings values
        self.assertIsNone(doc["last_ping"])
        self.assertEqual(doc["n_pings"], 0)

        self.assertEqual(Check.objects.count(), 1)
        check = Check.objects.get()
        self.assertEqual(check.name, "Foo")
        self.assertEqual(check.tags, "bar,baz")
        self.assertEqual(check.timeout.total_seconds(), 3600)
        self.assertEqual(check.grace.total_seconds(), 60)

    def test_it_accepts_api_key_in_header(self):
        payload = json.dumps({"name": "Foo"})

        ### Make the post request and get the response
        r = self.client.post(
            self.URL,
            payload,
            HTTP_X_API_KEY='abc',
            content_type='application/json'
        )

        self.assertEqual(r.status_code, 201)

    def test_it_handles_missing_request_body(self):
        ### Make the post request with a missing body and get the response
        r = self.client.post(self.URL, content_type='application/json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["error"], "wrong api_key")

    def test_it_handles_invalid_json(self):
        ### Make the post request with invalid json data type
        response = self.client.post(
            self.URL, 'some data',
            content_type='application/json',
            HTTP_X_API_KEY='abc'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "could not parse request body")

    def test_it_rejects_wrong_api_key(self):
        self.post({"api_key": "wrong"},
                  expected_error="wrong api_key")

    def test_it_rejects_non_number_timeout(self):
        self.post({"api_key": "abc", "timeout": "oops"},
                  expected_error="timeout is not a number")

    def test_it_rejects_non_string_name(self):
        self.post({"api_key": "abc", "name": False},
                  expected_error="name is not a string")

    ### Test for the 'timeout is too small' and 'timeout is too large' errors
    def test_it_rejects_timeout_too_small(self):
        """
        Ensures that a small timeout is rejected
        """
        response = self.client.post(
            reverse('hc-api-checks'),
            json.dumps({"api_key": "abc", "timeout": 50}),
            content_type="application/json"
        )

        # Assert that the timeout is flagged as being too small
        response_payload = response.json()
        self.assertEqual(response_payload["error"], "timeout is too small")

    def test_it_rejects_timeout_too_large(self):
        """
        Ensure that too large a timeout is rejected
        """
        response = self.client.post(
            reverse('hc-api-checks'),
            json.dumps({"api_key": "abc", "timeout": 10000000000}),
            content_type="application/json"
        )
        response_payload = response.json()

        # assert that an error is raised that the timeout is too large
        self.assertEqual(response_payload["error"], "timeout is too large")

    ### Test for the assignment of channels
    def test_it_assigns_channels(self):
        """
        This test ensure that checks are assigned the user's channels
        """
        # Create channel for user Alice
        channel = Channel(user=self.alice)
        channel.save()

        # Create a check for user Alice
        request_payload = {
            "api_key": "abc",
            "name": "Foo",
            "tags": "bar,baz",
            "timeout": 3600,
            "grace": 60
        }
        response_payload = self.post(request_payload)
        self.assertEqual(response_payload.status_code, 201)

        # Assign the check all of Alice's channels
        check = Check.objects.get(user=self.alice, name="Foo")
        check.assign_all_channels()

        # Assert channel was assigned
        self.assertEqual(check.channel_set.count(), 1)
