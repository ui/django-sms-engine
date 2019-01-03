from django.db import connection
from django.test import TransactionTestCase

from mock import patch

from sms_engine.models import SMS, PRIORITY, STATUS, Log, Backend
from sms_engine.sms import create as create_sms, send as send_sms, _send_bulk, get_queued


class SMSTest(TransactionTestCase):

    def test_get_queued_sms_respecting_priority(self):
        sms1 = create_sms(to="+62800000000001", message="Test", backend='dummy')
        sms2 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                          priority=PRIORITY.high)
        self.assertEqual([sms2, sms1], list(get_queued()))

    def test_sms_create(self):
        create_sms(to="+62800000000001", message="Test", backend='dummy')
        sms = SMS.objects.latest('id')
        self.assertEqual(sms.to, '+62800000000001')
        self.assertEqual(sms.message, 'Test')

        # default priority is medium
        self.assertEqual(sms.priority, PRIORITY.medium)
        # if priority != now, default status is set as queued
        self.assertEqual(sms.status, STATUS.queued)

        self.assertRaises(
            ValueError, create_sms, to="+62800000000001", message="Test",
            backend="unavailable_backends"
        )

    @patch('sms_engine.models.SMS.dispatch')
    def test_sms_send(self, mock):
        send_sms(to="+62800000000001", message="Test Send", backend='dummy')
        sms = SMS.objects.latest('id')
        self.assertEqual(sms.to, '+62800000000001')
        self.assertEqual(sms.message, 'Test Send')
        self.assertEqual(sms.status, STATUS.queued)
        self.assertEqual(mock.call_count, 0)

        send_sms(to="+62800000000002", message="Test Send", backend='dummy', priority=PRIORITY.now)
        sms = SMS.objects.latest('id')
        self.assertEqual(sms.to, '+62800000000002')
        # dispatch method should be called if priority is `now`
        self.assertEqual(mock.call_count, 1)

    def test_send_bulk_sms(self):
        # sent smses
        backend = Backend.objects.create(alias="dummy")
        for i in range(0, 24):
            SMS.objects.create(
                to='+6280000000000', message='test', backend_alias='dummy'
            )
        _send_bulk(SMS.objects.all(), log_level=2)
        self.assertEqual(
            SMS.objects.filter(to='+6280000000000', status=STATUS.sent).count(), 24
        )
        self.assertEqual(
            Log.objects.filter(status=STATUS.sent).count(), 24
        )

        # Failed smses
        backend.alias = "error"
        backend.save()
        SMS.objects.all().delete()

        for i in range(0, 6):
            SMS.objects.create(
                to='+6280000000000', message='test', backend_alias='error'
            )
        _send_bulk(SMS.objects.all(), log_level=2)
        self.assertEqual(
            SMS.objects.filter(to='+6280000000000', status=STATUS.failed).count(), 6
        )

        # make sure logs for failed smss created properly
        self.assertEqual(
            Log.objects.filter(status=STATUS.failed).count(), 6
        )