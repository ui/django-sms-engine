from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from mock import patch

from sms_engine import sms
from sms_engine.models import SMS, STATUS, PRIORITY, Backend
from sms_engine.settings import get_backend, get_available_backends
from sms_engine.backends import DummyBackend
from sms_engine.tests.backends import Always153Backend, DynamicBackend


class BackendTest(TestCase):

    def test_email_backend(self):
        """
        Ensure that email backend properly queue email messages.
        """
        sms.send(to="+62800000000001", message="Test", backend='dummy')
        sms_ = SMS.objects.latest('id')
        self.assertEqual(sms_.to, '+62800000000001')
        self.assertEqual(sms_.status, STATUS.queued)
        self.assertEqual(sms_.priority, PRIORITY.medium)

    def test_email_backend_settings(self):
        self.maxDiff = None

        self.assertEqual(get_available_backends(), {
            'default': 'sms_engine.backends.DummyBackend',
            'dummy': 'sms_engine.backends.DummyBackend',
            'always153': 'sms_engine.tests.backends.Always153Backend',
            'error': 'sms_engine.backends.RaiseExceptionBackend',
            'dynamic-test123': {
                'CLASS': 'sms_engine.tests.backends.DynamicBackend',
                'usr': 'test123',
                'pwd': 'test456',
            },
            'dynamic-proper-sender': {
                'CLASS': 'sms_engine.tests.backends.DynamicBackend',
                'usr': 'proper-sender',
                'pwd': 'proper-password',
            }
        })

        self.assertTrue(isinstance(get_backend('always153'), Always153Backend))

        # No parameter to `get_backend` means you want the default
        self.assertTrue(isinstance(get_backend(), DummyBackend))

        # Empty backends should always raise improper configured error
        with self.settings(SMS_ENGINE={}):
            self.assertRaises(ImproperlyConfigured, get_backend)

        with self.settings(SMS_ENGINE={}):
            self.assertRaises(ImproperlyConfigured, get_backend, 'always153')

        # SMS_ENGINE should not work if no default backend declared
        with self.settings(SMS_ENGINE={'BACKENDS': {'dummy': 'sms_engine.backends.DummyBackend'}}):
            self.assertRaises(ImproperlyConfigured, get_backend)

    def test_dynamic_backends_with_kwargs(self):
        test123_backend = get_backend('dynamic-test123')

        # Validate type and kwargs are sent correctly
        self.assertTrue(isinstance(test123_backend, DynamicBackend))
        self.assertEqual(
            test123_backend.kwargs,
            {'CLASS': 'sms_engine.tests.backends.DynamicBackend',
             'usr': 'test123', 'pwd': 'test456'})

        # We have another sender, but using the same backend
        proper_sender_backend = get_backend('dynamic-proper-sender')

        # Validate type and kwargs are sent correctly
        self.assertTrue(isinstance(proper_sender_backend, DynamicBackend))
        self.assertEqual(
            proper_sender_backend.kwargs,
            {'CLASS': 'sms_engine.tests.backends.DynamicBackend',
             'usr': 'proper-sender',
             'pwd': 'proper-password'})

    def test_flatten_backends(self):
        backends = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: ['anomali_twilio'],
            Backend.PRIORITY.low: ['anomali_ims'],
        }

        flattened = Backend.flatten(backends)
        self.assertIn('anomali_nadyne', flattened)
        self.assertIn('anomali_jatis', flattened)
        self.assertIn('anomali_twilio', flattened)
        self.assertIn('anomali_ims', flattened)

        # Repeat backends until min_backends
        backends = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        flattened = Backend.flatten(backends, min_backends=5)
        self.assertEqual(len(flattened), 5)
        self.assertIn('anomali_nadyne', flattened)
        self.assertIn('anomali_jatis', flattened)
        self.assertNotIn('anomali_twilio', flattened)
        self.assertNotIn('anomali_ims', flattened)

        backends = {
            Backend.PRIORITY.high: ['anomali_nadyne'],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        flattened = Backend.flatten(backends, min_backends=5)
        expected_flattened = ['anomali_nadyne', 'anomali_nadyne', 'anomali_nadyne',
                              'anomali_nadyne', 'anomali_nadyne']
        self.assertEqual(flattened, expected_flattened)

        # Empty backends, empty list should be returned
        backends = {
            Backend.PRIORITY.high: [],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        flattened = Backend.flatten(backends, min_backends=5)
        self.assertEqual(flattened, [])

    @patch('sms_engine.cached_backend.delete')
    def test_backend_cache_busting(self, delete_mock):
        self.assertEqual(delete_mock.call_count, 0)

        # Any changes should bust cache
        anomali_twilio = Backend.objects.create(alias='anomali_twilio', priority=Backend.PRIORITY.normal)
        self.assertEqual(delete_mock.call_count, 1)

        anomali_twilio.priority = 1
        anomali_twilio.save()
        self.assertEqual(delete_mock.call_count, 2)