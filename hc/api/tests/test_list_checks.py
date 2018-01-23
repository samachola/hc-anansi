import json
from datetime import timedelta as td
from django.utils.timezone import now
from django.conf import settings
from django.urls import reverse

from hc.api.models import Check
from hc.test import BaseTestCase


class ListChecksTestCase(BaseTestCase):

    def setUp(self):
        super(ListChecksTestCase, self).setUp()

        self.now = now().replace(microsecond=0)

        self.a1 = Check(user=self.alice, name="Alice 1")
        self.a1.timeout = td(seconds=3600)
        self.a1.grace = td(seconds=900)
        self.a1.last_ping = self.now
        self.a1.n_pings = 1
        self.a1.status = "new"
        self.a1.save()

        self.a2 = Check(user=self.alice, name="Alice 2")
        self.a2.timeout = td(seconds=86400)
        self.a2.grace = td(seconds=86400)
        self.a2.last_ping = self.now
        self.a2.status = "up"
        self.a2.save()

    def get(self):
        return self.client.get("/api/v1/checks/", HTTP_X_API_KEY="abc")

    def test_it_works(self):
        r = self.get()
        ### Assert the response status code
        self.assertEqual(r.status_code, 200)

        doc = r.json()
        self.assertTrue("checks" in doc)

        checks = {check["name"]: check for check in doc["checks"]}
        ### Assert the expected length of checks
        self.assertEqual(len(checks), 2)
        ### Assert the checks Alice 1 and Alice 2's timeout, grace, ping_url, status,
        ### last_ping, n_pings and pause_url

        pause_url = reverse('hc-api-pause', args=[self.a1.code])
        pause_url = settings.SITE_ROOT + pause_url
        # assertions for Alice 1 -> [a1]
        alice_1 = checks["Alice 1"]
        alice_check_1 = dict(
            timeout=alice_1["timeout"],
            grace=alice_1["grace"],
            status=alice_1["status"],
            last_ping=alice_1["last_ping"],
            n_pings=alice_1["n_pings"],
            ping_url=alice_1["ping_url"],
            pause_url=alice_1["pause_url"],
        )
        expected_results = dict(
            timeout=3600,
            grace=900,
            status="new",
            last_ping=self.a1.last_ping.isoformat(),
            n_pings=1,
            ping_url=str(self.a1.url()),
            pause_url=pause_url
        )
        self.assertEqual(alice_check_1, expected_results)
        # assertions for Alice 2 -> [a2]
        alice_2 = checks["Alice 2"]
        alice_check_2 = dict(
            timeout=alice_2["timeout"],
            grace=alice_2["grace"],
            status=alice_2["status"],
            last_ping=alice_2["last_ping"],
            n_pings=alice_2["n_pings"],
            ping_url=alice_2["ping_url"],
            pause_url=alice_2["pause_url"],
        )
        pause_url = reverse("hc-api-pause", args=[self.a2.code])
        pause_url = settings.SITE_ROOT + pause_url
        expected_results = dict(
            timeout=86400,
            grace=86400,
            status="up",
            last_ping=self.a2.last_ping.isoformat(),
            n_pings=0,
            ping_url=str(self.a2.url()),
            pause_url=pause_url
        )
        self.assertEqual(alice_check_2, expected_results)


    def test_it_shows_only_users_checks(self):
        bobs_check = Check(user=self.bob, name="Bob 1")
        bobs_check.save()

        r = self.get()
        data = r.json()
        self.assertEqual(len(data["checks"]), 2)
        for check in data["checks"]:
            self.assertNotEqual(check["name"], "Bob 1")

    ### Test that it accepts an api_key in the request
    def test_it_accepts_api_key_in_request(self):
        """
        This test ensures that the api checks resource accepts an
        api_key in the request
        """
        payload = json.dumps(
            {
                "api_key": "abc"
            }
        )
        response = self.client.generic(
            "GET", reverse("hc-api-checks"),
            payload, content_type='application/json'
        )

        response_payload = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue("checks" in response_payload)
