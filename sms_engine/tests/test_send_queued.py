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

        # Make sure bulk sms runs successfully
        smses = []
        for i in range(0, 300):
            # create 3 failed sms
            if i % 100 == 0:
                sms = SMS(to='+6280000000000', status=STATUS.queued, backend_alias='error')
            else:
                sms = SMS(to='+6280000000000', status=STATUS.queued, backend_alias='dummy')
            smses.append(sms)

        SMS.objects.bulk_create(smses)

        call_command('send_queued_sms')

        self.assertEqual(SMS.objects.filter(status=STATUS.sent).count(), 297)
        self.assertEqual(SMS.objects.filter(status=STATUS.failed).count(), 3)

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

    def test_empty_backend_alias(self):
        """
        Empty backend alias shouldn't cause infinite loop
        """
        # Empty backend alias will point to `default` backend
        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued)
        call_command('send_queued_sms', log_level=0)
        self.assertEqual(sms.logs.count(), 0)
        sms.refresh_from_db()
        self.assertEqual(sms.status, STATUS.sent)

        # No extra logs generated
        sms = SMS.objects.create(to='+6280000000000', status=STATUS.queued)
        call_command('send_queued_sms', log_level=1)
        self.assertEqual(sms.logs.count(), 0)
        sms.refresh_from_db()
        self.assertEqual(sms.status, STATUS.sent)
