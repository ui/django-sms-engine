from django.test import TransactionTestCase

from sms_engine import cached_backend
from sms_engine.models import Backend


class BackendTest(TransactionTestCase):

    def test_cached_backend_get(self):
        # Empty aliases
        expected = {
            Backend.PRIORITY.high: [],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        self.assertEqual(cached_backend.get(use_cache=False), expected)

        # multiple backends
        Backend.objects.create(alias='anomali_nadyne', priority=0)
        Backend.objects.create(alias='anomali_jatis', priority=0)
        anomali_twilio = Backend.objects.create(alias='anomali_twilio', priority=1)
        anomali_ims = Backend.objects.create(alias='anomali_ims', priority=2)

        expected = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: ['anomali_twilio'],
            Backend.PRIORITY.low: ['anomali_ims'],
        }
        self.assertEqual(cached_backend.get(use_cache=False), expected)

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
        self.assertEqual(cached_backend.get(use_cache=False), expected)