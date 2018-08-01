from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from sms_engine import sms
from sms_engine.models import SMS, STATUS, PRIORITY
from sms_engine.settings import get_backend, get_available_backends
from sms_engine.backends import Always153Backend, DynamicBackend, DummyBackend


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
        print(get_available_backends())
        self.maxDiff = None

        self.assertEqual(get_available_backends(), {
            'default': 'sms_engine.backends.DummyBackend',
            'dummy': 'sms_engine.backends.DummyBackend',
            'always153': 'sms_engine.backends.Always153Backend',
            'error': 'sms_engine.backends.RaiseExceptionBackend',
            'dynamic-test123': {
                'CLASS': 'sms_engine.backends.DynamicBackend',
                'usr': 'test123',
                'pwd': 'test456',
            },
            'dynamic-proper-sender': {
                'CLASS': 'sms_engine.backends.DynamicBackend',
                'usr': 'proper-sender',
                'pwd': 'proper-password',
            }
        })

        self.assertEqual(type(get_backend('always153')), Always153Backend)

        # No parameter to `get_backend` means you want the default
        self.assertEqual(type(get_backend()), DummyBackend)

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
        self.assertEqual(type(test123_backend), DynamicBackend)
        self.assertEqual(
            test123_backend.kwargs,
            {'CLASS': 'sms_engine.backends.DynamicBackend', 'usr': 'test123', 'pwd': 'test456'})

        # We have another sender, but using the same backend
        proper_sender_backend = get_backend('dynamic-proper-sender')

        # Validate type and kwargs are sent correctly
        self.assertEqual(type(proper_sender_backend), DynamicBackend)
        self.assertEqual(
            proper_sender_backend.kwargs,
            {'CLASS': 'sms_engine.backends.DynamicBackend', 'usr': 'proper-sender', 'pwd': 'proper-password'})

