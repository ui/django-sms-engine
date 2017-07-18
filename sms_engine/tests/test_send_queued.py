from django.core.management import call_command
from django.test import TestCase

from ..models import SMS, STATUS


class CommandTest(TestCase):

    def test_send_queued_mail(self):
        """
        Quick check that ``send_queued_sms`` doesn't error out.
        """
        # Make sure that send_queued_sms with empty queue does not raise error
        call_command('send_queued_sms')

        SMS.objects.create(to='+6280000000000', status=STATUS.queued, backend_alias='dummy')
        call_command('send_queued_sms')

        self.assertEqual(SMS.objects.filter(status=STATUS.sent).count(), 1)

    def test_successful_deliveries_logging(self):
        """
        Successful deliveries are only logged when log_level is 2.
        """
        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued,
                                 backend_alias='dummy')
        call_command('send_queued_sms', log_level=0)
        self.assertEqual(sms.logs.count(), 0)

        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued,
                                 backend_alias='dummy')
        call_command('send_queued_sms', log_level=1)
        self.assertEqual(sms.logs.count(), 0)

        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued,
                                 backend_alias='dummy')
        call_command('send_queued_sms', log_level=2)
        self.assertEqual(sms.logs.count(), 1)

    def test_failed_deliveries_logging(self):
        """
        Failed deliveries are logged when log_level is 1 and 2.
        """
        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued,
                                 backend_alias='error')
        call_command('send_queued_sms', log_level=0)
        self.assertEqual(sms.logs.count(), 0)

        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued,
                                 backend_alias='error')
        call_command('send_queued_sms', log_level=1)
        self.assertEqual(sms.logs.count(), 1)

        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued,
                                 backend_alias='error')
        call_command('send_queued_sms', log_level=2)
        self.assertEqual(sms.logs.count(), 1)
