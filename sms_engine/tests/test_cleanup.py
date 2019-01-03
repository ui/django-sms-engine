import datetime

from django.core.management import call_command
from django.db import connection
from django.test import TransactionTestCase
from django.utils.timezone import now

from ..models import Log, SMS, STATUS


class CommandTest(TransactionTestCase):

    def test_cleanup_sms(self):
        """
        The ``cleanup_sms`` command deletes smses older than a specified
        amount of days
        """
        self.assertEqual(SMS.objects.count(), 0)

        # The command shouldn't delete today's sms
        sms = SMS.objects.create(to="+6280000000000", message="test", status=STATUS.sent)
        sms.logs.create(status=1, message='Test')

        call_command('cleanup_sms', days=30)
        self.assertEqual(SMS.objects.count(), 1)
        self.assertEqual(Log.objects.count(), 1)

        # SMS older than 30 days should be deleted
        sms.created = now() - datetime.timedelta(31)
        sms.save()
        call_command('cleanup_sms', days=30)
        self.assertEqual(SMS.objects.count(), 0)
        self.assertEqual(Log.objects.count(), 0)