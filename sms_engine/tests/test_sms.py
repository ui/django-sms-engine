from datetime import time, timedelta

from freezegun import freeze_time
from mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from sms_engine.models import SMS, PRIORITY, STATUS, Log
from sms_engine.sms import create as create_sms, send as send_sms, _send_bulk, get_queued


class SMSTest(TestCase):

    def test_delivery_window(self):
        sms1 = create_sms(to="+62800000000001", message="Test", backend='dummy')
        sms2 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                          delivery_window=(time(10, 0), time(22, 0)))

        # 7 AM, 07:00+7
        with freeze_time("2000-1-1 00:00:00", tz_offset=7):
            self.assertEqual([sms1], list(get_queued()))

        # 10 AM, 10:00+7
        with freeze_time("2000-1-1 03:00:00", tz_offset=7):
            self.assertEqual([sms1, sms2], list(get_queued()))

        # 11 PM, 23:00+7
        with freeze_time("2000-1-1 16:00:00", tz_offset=7):
            self.assertEqual([sms1], list(get_queued()))

        # 7 AM, 07:00
        SMS.objects.all().delete()
        with freeze_time("2000-1-1 00:00:00", tz_offset=7):
            sms1 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                              delivery_window=(time(7, 1), time(22, 0)))
            sms2 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                              delivery_window=(time(7, 0), time(22, 0)))
            self.assertEqual([sms2], list(get_queued()))

        # Every combination of these case is valid
        SMS.objects.all().delete()
        with freeze_time("2000-1-1 00:00:00", tz_offset=7):
            sms1 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                              delivery_window=(time(6, 0), time(22, 0)))
            sms2 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                              delivery_window=(time(7, 0), time(22, 0)))
            sms3 = create_sms(to="+62800000000001", message="Test", backend='dummy')
            sms4 = create_sms(to="+62800000000001", message="Test", backend='dummy',
                              scheduled_time=timezone.localtime(timezone.now()) - timedelta(minutes=1))
            self.assertEqual([sms1, sms2, sms3, sms4], list(get_queued()))

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
        self.assertEqual(sms.start_of_delivery_window, None)
        self.assertEqual(sms.end_of_delivery_window, None)

        self.assertRaises(
            ValueError, create_sms, to="+62800000000001", message="Test",
            backend="unavailable_backends"
        )

        # Wrong format
        self.assertRaises(
            ValueError, create_sms, to="+62800000000001", message="Test",
            backend="dummy", delivery_window=(None, 1)
        )

        # Start bigger than end
        self.assertRaises(
            ValueError, create_sms, to="+62800000000001", message="Test",
            backend="dummy", delivery_window=(time(20, 0), time(10, 0))
        )

        create_sms(to="+62800000000002", message="Test", backend='dummy',
                   delivery_window=(time(10, 0), time(20, 0)))

        sms = SMS.objects.latest('id')
        self.assertEqual(sms.to, '+62800000000002')
        self.assertEqual(sms.message, 'Test')

        # default priority is medium
        self.assertEqual(sms.priority, PRIORITY.medium)
        # if priority != now, default status is set as queued
        self.assertEqual(sms.status, STATUS.queued)
        self.assertEqual(sms.start_of_delivery_window, time(10, 0))
        self.assertEqual(sms.end_of_delivery_window, time(20, 0))

        with override_settings(USE_TZ=False):
            # This works
            create_sms(to="+62800000000002", message="Test", backend='dummy')

            # This is not supported currently
            self.assertRaises(
                ValueError, create_sms, to="+62800000000001", message="Test",
                backend="dummy", delivery_window=(time(10, 0), time(20, 0))
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
        for i in range(0, 30):
            # Create 6 error smss
            if i % 5 == 0:
                SMS.objects.create(
                    to='+6280000000000', message='test', backend_alias='error'
                )
            else:
                SMS.objects.create(
                    to='+6280000000000', message='test', backend_alias='dummy'
                )

        _send_bulk(SMS.objects.all(), log_level=2)

        self.assertEqual(
            SMS.objects.filter(to='+6280000000000', status=STATUS.sent).count(), 24
        )
        self.assertEqual(
            SMS.objects.filter(to='+6280000000000', status=STATUS.failed).count(), 6
        )

        # make sure logs for failed smss created properly
        self.assertEqual(
            Log.objects.filter(status=STATUS.failed).count(), 6
        )
        self.assertEqual(
            Log.objects.filter(status=STATUS.sent).count(), 24
        )
