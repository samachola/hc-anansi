from django.core import mail
from hc.api.models import Check
from hc.test import BaseTestCase
from django.utils import timezone
from datetime import timedelta
from mock import patch
from django.core.management import call_command
from hc.api.management.commands.sendreports import Command
from hc.accounts.models import Profile


class SendReportsTestCase(BaseTestCase):

    def test_it_sends_report_daily(self):
        # self.client.login(username="alice@example.org", password="password")
        
        check = Check(name="Test Check", user=self.alice)
        check.last_ping = timezone.now()
        check.save()

        self.profile.reports_allowed = 'Daily'
        now = timezone.now()
        self.profile.date_joined = now - timedelta(days=1)
        self.profile.save()

        result = call_command('sendreports')
        self.assertEqual(result, 'Sent 1 reports') 

        #Assert that the email was sent and check email content
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Daily Report')

    def test_sends_reports_weekly(self):
        check = Check(name="Test Check", user=self.alice)
        check.last_ping = timezone.now()
        check.save()

        self.profile.reports_allowed = 'Weekly'
        now = timezone.now()
        self.profile.date_joined = now - timedelta(days=7)

        self.profile.save()

        result = call_command('sendreports')
        self.assertEqual(result, 'Sent 1 reports') 

        #Assert that the email was sent and check email content
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Weekly Report')
        
    def test_sends_reports_monthly(self):
        check = Check(name="Test Check", user=self.alice)
        check.last_ping = timezone.now()
        check.save()

        self.profile.reports_allowed = 'Monthly'
        now = timezone.now()
        self.profile.date_joined = now - timedelta(days=30)

        self.profile.save()

        result = call_command('sendreports')
        self.assertEqual(result, 'Sent 1 reports') 

        #Assert that the email was sent and check email content
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Monthly Report')
