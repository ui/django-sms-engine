from django.test import TestCase

from unittest.mock import patch
from sms_engine import cached_backend
from sms_engine.models import Backend


class BackendTest(TestCase):

    def test_cached_backend_get(self):
        # Empty aliases
        expected = {
            Backend.PRIORITY.high: [],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        self.assertEqual(cached_backend.get(cache=False), expected)

        # multiple backends
        Backend.objects.create(alias='anomali_nadyne', priority=Backend.PRIORITY.high)
        Backend.objects.create(alias='anomali_jatis', priority=Backend.PRIORITY.high)
        anomali_twilio = Backend.objects.create(alias='anomali_twilio', priority=Backend.PRIORITY.normal)
        anomali_ims = Backend.objects.create(alias='anomali_ims', priority=Backend.PRIORITY.low)

        expected = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: ['anomali_twilio'],
            Backend.PRIORITY.low: ['anomali_ims'],
        }
        self.assertEqual(cached_backend.get(cache=False), expected)

        # Inactive backends should not be returned
        anomali_twilio.is_active = False
        anomali_twilio.save()
        anomali_ims.is_active = False
        anomali_ims.save()
        expected = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        self.assertEqual(cached_backend.get(cache=False), expected)

    @patch('sms_engine.cached_backend.delete')
    def test_backend_cache_busting(self, delete_mock):
        self.assertEqual(delete_mock.call_count, 0)

        # Any changes should bust cache
        anomali_twilio = Backend.objects.create(alias='anomali_twilio', priority=Backend.PRIORITY.normal)
        self.assertEqual(delete_mock.call_count, 1)

        anomali_twilio.priority = Backend.PRIORITY.low
        anomali_twilio.save()
        self.assertEqual(delete_mock.call_count, 2)