from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from sms_engine import sms
from sms_engine.models import SMS, STATUS, PRIORITY
from sms_engine.settings import get_backend, get_available_backends


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
        self.assertEqual(get_backend('nadyne'), 'sms_engine.backends.NadyneBackend')
        self.assertEqual(get_available_backends(), {
            'default': 'sms_engine.backends.DummyBackend',
            'dummy': 'sms_engine.backends.DummyBackend',
            'twilio': 'sms_engine.backends.TwilioBackend',
            'nadyne': 'sms_engine.backends.NadyneBackend',
            'error': 'sms_engine.backends.RaiseExceptionBackend',
        })

        with self.settings(SMS_ENGINE={}):
            # If no sms backend is set, backend should default to Twilio Backend
            self.assertEqual(get_backend(), 'sms_engine.backends.TwilioBackend')

            # if no backend is set, get_available_backends() always return twilio backend by default
            self.assertEqual(get_available_backends(), {'default': 'sms_engine.backends.TwilioBackend'})

        # get_backend should handle empty string correctly
        self.assertEqual(get_backend(''), 'sms_engine.backends.DummyBackend')

        # SMS_ENGINE should not work if no default backend declared
        with self.settings(SMS_ENGINE={'BACKENDS': {'dummy': 'sms_engine.backends.DummyBackend'}}):
            self.assertRaises(ImproperlyConfigured, get_backend)
